"""ITU inspired topology routing for the isolated attenuation ablation.

This module does not modify the deployed Try 78 or Try 80 prior. It estimates
the three morphology descriptors used by ITU-R P.1410 from a raster topology
map and assigns the map to the closest standard environment prototype.
"""

from __future__ import annotations

import math
import hashlib
from dataclasses import asdict, dataclass
from typing import Dict, Mapping, Tuple

import numpy as np
from scipy import ndimage


ITU_PROTOTYPES: Mapping[str, Tuple[float, float, float]] = {
    "suburban": (0.1, 750.0, 8.0),
    "urban": (0.3, 500.0, 15.0),
    "dense_urban": (0.5, 300.0, 20.0),
    "urban_highrise": (0.5, 300.0, 50.0),
}


@dataclass(frozen=True)
class ITUMorphology:
    alpha: float
    beta_buildings_per_km2: float
    gamma_mode_m: float
    component_count: int
    map_area_km2: float
    mean_nonzero_height_m: float
    mean_building_max_height_m: float
    raw_environment: str
    routed_environment: str
    prototype_log_distance: float

    def to_dict(self) -> Dict[str, float | int | str]:
        return asdict(self)


def _structure(connectivity: int) -> np.ndarray:
    if connectivity == 4:
        return ndimage.generate_binary_structure(2, 1)
    if connectivity == 8:
        return ndimage.generate_binary_structure(2, 2)
    raise ValueError(f"connectivity must be 4 or 8, got {connectivity}")


def estimate_itu_parameters(
    topology: np.ndarray,
    *,
    meters_per_pixel: float = 1.0,
    connectivity: int = 4,
    min_component_area_m2: float = 1.0,
) -> Tuple[float, float, float, int, float, float, float]:
    """Estimate alpha, beta, and gamma from one building-height raster.

    alpha is the occupied area fraction. beta is approximated by connected
    building footprints per square kilometre. gamma is the Rayleigh maximum
    likelihood scale, which is also the mode, fitted to one building height
    per connected footprint. For this raster translation, building height is
    the maximum topology value inside the footprint.
    """

    topo = np.asarray(topology, dtype=np.float32)
    if topo.ndim != 2:
        raise ValueError(f"expected a 2D topology map, got shape {topo.shape}")
    if meters_per_pixel <= 0:
        raise ValueError("meters_per_pixel must be positive")
    if min_component_area_m2 <= 0:
        raise ValueError("min_component_area_m2 must be positive")

    finite = np.isfinite(topo)
    building_mask = finite & (topo > 0.0)
    alpha = float(building_mask.mean())
    map_area_km2 = float(topo.size * meters_per_pixel**2 / 1_000_000.0)
    if not np.any(building_mask):
        return alpha, 0.0, 0.0, 0, map_area_km2, 0.0, 0.0

    labels, component_count_all = ndimage.label(
        building_mask, structure=_structure(connectivity)
    )
    component_ids = np.arange(1, component_count_all + 1, dtype=np.int32)
    component_pixels = np.bincount(labels.ravel(), minlength=component_count_all + 1)[1:]
    keep = component_pixels.astype(np.float64) * meters_per_pixel**2 >= min_component_area_m2
    kept_ids = component_ids[keep]
    component_count = int(kept_ids.size)

    beta = component_count / max(map_area_km2, 1e-12)
    if component_count:
        building_heights = np.asarray(
            ndimage.maximum(topo, labels=labels, index=kept_ids), dtype=np.float64
        )
        building_heights = building_heights[
            np.isfinite(building_heights) & (building_heights > 0.0)
        ]
        gamma = (
            float(math.sqrt(float(np.mean(np.square(building_heights))) / 2.0))
            if building_heights.size
            else 0.0
        )
        mean_building_max_height = (
            float(building_heights.mean()) if building_heights.size else 0.0
        )
    else:
        gamma = 0.0
        mean_building_max_height = 0.0

    mean_nonzero_height = float(topo[building_mask].mean())
    return (
        alpha,
        beta,
        gamma,
        component_count,
        map_area_km2,
        mean_nonzero_height,
        mean_building_max_height,
    )


def nearest_itu_environment(
    alpha: float,
    beta_buildings_per_km2: float,
    gamma_mode_m: float,
) -> Tuple[str, float]:
    """Return the closest standard prototype using equal log-ratio errors."""

    observed = np.maximum(
        np.asarray([alpha, beta_buildings_per_km2, gamma_mode_m], dtype=np.float64),
        1e-6,
    )
    distances: Dict[str, float] = {}
    for name, values in ITU_PROTOTYPES.items():
        reference = np.asarray(values, dtype=np.float64)
        distances[name] = float(np.linalg.norm(np.log(observed / reference)))
    selected = min(distances, key=distances.get)
    return selected, distances[selected]


class ITUTopologyRouter:
    """Callable topology router with caching for repeated city rasters."""

    def __init__(
        self,
        *,
        mode: str = "itu3",
        meters_per_pixel: float = 1.0,
        connectivity: int = 4,
        min_component_area_m2: float = 1.0,
    ) -> None:
        if mode not in {"itu2", "itu3", "itu4"}:
            raise ValueError(f"unsupported routing mode: {mode}")
        self.mode = mode
        self.meters_per_pixel = float(meters_per_pixel)
        self.connectivity = int(connectivity)
        self.min_component_area_m2 = float(min_component_area_m2)
        self._cache: Dict[Tuple[object, ...], ITUMorphology] = {}

    @staticmethod
    def _cache_key(topology: np.ndarray) -> Tuple[object, ...]:
        topo = np.ascontiguousarray(topology, dtype=np.float32)
        digest = hashlib.blake2b(topo.view(np.uint8), digest_size=16).hexdigest()
        return (
            topo.shape,
            digest,
        )

    def describe(self, topology: np.ndarray) -> ITUMorphology:
        key = self._cache_key(topology)
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        (
            alpha,
            beta,
            gamma,
            count,
            area,
            mean_height,
            mean_building_max_height,
        ) = estimate_itu_parameters(
            topology,
            meters_per_pixel=self.meters_per_pixel,
            connectivity=self.connectivity,
            min_component_area_m2=self.min_component_area_m2,
        )
        raw_environment, distance = nearest_itu_environment(alpha, beta, gamma)
        if self.mode == "itu2":
            routed_environment = (
                "suburban" if raw_environment == "suburban" else "urban_or_denser"
            )
        elif self.mode == "itu3":
            routed_environment = (
                "dense_urban"
                if raw_environment in {"dense_urban", "urban_highrise"}
                else raw_environment
            )
        else:
            routed_environment = raw_environment

        result = ITUMorphology(
            alpha=alpha,
            beta_buildings_per_km2=beta,
            gamma_mode_m=gamma,
            component_count=count,
            map_area_km2=area,
            mean_nonzero_height_m=mean_height,
            mean_building_max_height_m=mean_building_max_height,
            raw_environment=raw_environment,
            routed_environment=routed_environment,
            prototype_log_distance=distance,
        )
        self._cache[key] = result
        return result

    def classify(self, topology: np.ndarray) -> str:
        return self.describe(topology).routed_environment

    @property
    def cached_topologies(self) -> int:
        return len(self._cache)

    def contract(self) -> Dict[str, object]:
        return {
            "mode": self.mode,
            "prototypes": {
                name: {
                    "alpha": values[0],
                    "beta_buildings_per_km2": values[1],
                    "gamma_mode_m": values[2],
                }
                for name, values in ITU_PROTOTYPES.items()
            },
            "assignment": "minimum equal-weight log-ratio distance to the four prototypes",
            "routing_merge": {
                "itu2": "urban, dense_urban, and urban_highrise are merged into urban_or_denser",
                "itu3": "urban_highrise is merged into dense_urban",
                "itu4": None,
            }[self.mode],
            "building_footprints": {
                "method": "connected components on topology > 0",
                "connectivity": self.connectivity,
                "minimum_component_area_m2": self.min_component_area_m2,
                "known_limitation": "touching raster footprints can be merged",
            },
            "gamma_definition": (
                "ITU-R P.1410-6 Rayleigh mode of the building-height distribution"
            ),
            "building_height_observation": (
                "one observation per connected footprint, equal to its maximum raster height"
            ),
            "gamma_estimator": (
                "Rayleigh maximum-likelihood scale sqrt(mean(building_max_height^2)/2)"
            ),
            "raster_interpretation_note": (
                "P.1410-6 defines a building-height distribution but does not prescribe "
                "mean-versus-maximum reduction for an irregular height raster"
            ),
            "meters_per_pixel": self.meters_per_pixel,
        }
