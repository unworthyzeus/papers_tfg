"""Evaluate the rho/phi ablation on the official test cities.

Every row keeps a recalibrated radial correction ``r(d2D, hTx)`` and the same
three-class ITU-conditioned NLoS calibration. The only change is whether the
coherent two-ray rho, phi, and bias terms are present.

No fitting is performed here. All calibrations were fitted previously on the
10,840 official training maps. This evaluator only reads the official test
split and writes compact aggregate results.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, Mapping, MutableMapping, Sequence

import h5py
import numpy as np

from itu_topology import ITUTopologyRouter


EXPERIMENT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TFG_ROOT = REPO_ROOT.parent
DEFAULT_HDF5 = DEFAULT_TFG_ROOT / "TFGpractice" / "Datasets" / "CKM_Dataset_270326.h5"
DEFAULT_REFERENCE_DIR = (
    DEFAULT_TFG_ROOT
    / "TFGpractice"
    / "TFGEightiethTry80"
    / "scripts"
    / "recalibrate_priors"
)
DEFAULT_TWO_RAY_DIR = EXPERIMENT_ROOT / "results" / "two_ray_itu3_building_max"
DEFAULT_RADIAL_DIR = EXPERIMENT_ROOT / "results" / "radial_only_itu3_building_max"
DEFAULT_OUTPUT = EXPERIMENT_ROOT / "results" / "rho_phi_ablation"
FINAL_FEATURES = tuple(range(1, 15))

COMBINATIONS = (
    ("with_rho_phi", True),
    ("without_rho_phi", False),
)


def import_reference_modules(reference_dir: Path):
    sys.path.insert(0, str(reference_dir))
    try:
        import run_try78_on_try80_split as official
        import try78_hybrid_path_loss_reference as hybrid_ref
        import try78_los_path_loss_prior as los_model
    finally:
        sys.path.pop(0)
    return official, hybrid_ref, los_model


def load_coefficients(path: Path) -> Dict[str, np.ndarray]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        key: np.asarray(value, dtype=np.float64)
        for key, value in payload["coefficients"].items()
    }


def load_radial_calibration(path: Path) -> Dict[str, np.ndarray]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        "height_bin_m": np.asarray([payload["height_bin_m"]], dtype=np.float32),
        "height_bins_m": np.asarray(payload["height_bins_m"], dtype=np.float32),
        "global_profile_db": np.asarray(payload["global_profile_db"], dtype=np.float32),
        "global_count": np.asarray(payload["global_count"], dtype=np.uint32),
        "radial_profile_db": np.asarray(payload["radial_profile_db"], dtype=np.float32),
        "radial_profile_smooth_db": np.asarray(
            payload["radial_profile_smooth_db"], dtype=np.float32
        ),
        "radial_count": np.asarray(payload["radial_count"], dtype=np.uint32),
    }


def fresh_stats() -> Dict[str, float | int]:
    return {"sse": 0.0, "n": 0}


def add_error(
    stats: MutableMapping[str, float | int],
    prediction: np.ndarray,
    target: np.ndarray,
    mask: np.ndarray,
) -> None:
    count = int(mask.sum())
    if count == 0:
        return
    error = prediction[mask].astype(np.float64) - target[mask].astype(np.float64)
    stats["sse"] = float(stats["sse"]) + float(error @ error)
    stats["n"] = int(stats["n"]) + count


def linear_nlos_map(
    features: np.ndarray,
    coefficient: np.ndarray,
    hybrid_ref,
) -> np.ndarray:
    selected = features[..., FINAL_FEATURES]
    prediction = np.einsum("ijk,k->ij", selected, coefficient, optimize=True)
    return np.clip(
        prediction,
        hybrid_ref.PATH_LOSS_MIN_DB,
        hybrid_ref.PATH_LOSS_MAX_DB,
    ).astype(np.float32)


def compute_cost231_map(height: float, hybrid_ref) -> np.ndarray:
    height_tx = max(float(height), 1.0)
    height_rx = max(float(hybrid_ref.RX_HEIGHT_M), 0.5)
    distance_2d = np.maximum(np.asarray(hybrid_ref._D2D, dtype=np.float64), 1.0)
    frequency_mhz = float(hybrid_ref.FREQ_GHZ) * 1000.0
    log_frequency = math.log10(frequency_mhz)
    mobile_correction = (
        (1.1 * log_frequency - 0.7) * height_rx
        - (1.56 * log_frequency - 0.8)
    )
    distance_km = np.maximum(distance_2d / 1000.0, 0.001)
    log_height = math.log10(height_tx)
    path_loss = (
        46.3
        + 33.9 * log_frequency
        - 13.82 * log_height
        - mobile_correction
        + (44.9 - 6.55 * log_height) * np.log10(distance_km)
        + 3.0
    )
    return np.clip(path_loss, 0.0, float(hybrid_ref.PATH_LOSS_MAX_DB)).astype(
        np.float32
    )


def rmse(stats: Mapping[str, float | int]) -> float:
    count = int(stats["n"])
    return math.sqrt(float(stats["sse"]) / count) if count else float("nan")


def write_csv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    rows = list(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    lines = [
        "# Rho/Phi ablation with fixed ITU topology conditioning",
        "",
        "All values are pixel-weighted RMSE in dB on the 2,590 official held-out test maps.",
        "Buildings are excluded. Every variant includes a radial correction `r(d2D, hTx)`",
        "recalibrated on the 10,840 official training maps.",
        "",
        "Both rows use the same three topology-specific NLoS ridge calibrations",
        "with per-sample ITU routing. Only rho, phi, and the two-ray bias change.",
        "",
        "| Scope | Rho/Phi | Maps | Overall RMSE | LoS RMSE | NLoS RMSE |",
        "|---|---|---:|---:|---:|---:|",
    ]
    scope_order = {"global": 0, "suburban": 1, "urban": 2, "dense_urban": 3}
    combination_order = {name: idx for idx, (name, _) in enumerate(COMBINATIONS)}
    ordered = sorted(
        rows,
        key=lambda row: (
            scope_order[str(row["scope"])],
            combination_order[str(row["combination"])],
        ),
    )
    for row in ordered:
        scope = str(row["scope"]).replace("_", " ").title()
        rho_phi = "With" if row["rho_phi"] == "with" else "Without"
        lines.append(
            f"| {scope} | {rho_phi} | {int(row['maps']):,} | "
            f"{float(row['overall_rmse_db']):.6f} | "
            f"{float(row['los_rmse_db']):.6f} | "
            f"{float(row['nlos_rmse_db']):.6f} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hdf5", type=Path, default=DEFAULT_HDF5)
    parser.add_argument("--reference-dir", type=Path, default=DEFAULT_REFERENCE_DIR)
    parser.add_argument("--two-ray-dir", type=Path, default=DEFAULT_TWO_RAY_DIR)
    parser.add_argument("--radial-dir", type=Path, default=DEFAULT_RADIAL_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--split-seed", type=int, default=42)
    parser.add_argument("--log-every", type=int, default=250)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    official, hybrid_ref, los_model = import_reference_modules(args.reference_dir)
    router = ITUTopologyRouter(
        mode="itu3",
        meters_per_pixel=float(hybrid_ref.METERS_PER_PIXEL),
        connectivity=4,
        min_component_area_m2=1.0,
    )
    hybrid_ref.sample_city_type = router.classify

    references = los_model.enumerate_samples(args.hdf5)
    train_refs, validation_refs, test_refs = official.split_city_holdout_try80(
        references,
        val_ratio=0.15,
        test_ratio=0.15,
        split_seed=args.split_seed,
    )
    print(
        f"official split: train={len(train_refs)}, validation={len(validation_refs)}, "
        f"test={len(test_refs)}",
        flush=True,
    )

    _, two_ray_calibration = los_model.load_calibration(
        args.two_ray_dir / "los_two_ray_refitted_calibration.json"
    )
    radial_calibration = load_radial_calibration(
        args.radial_dir / "los_radial_only_calibration.json"
    )
    regime_coefficients = load_coefficients(
        args.two_ray_dir / "nlos_regime_calibration_itu.json"
    )
    scopes = ("global", "suburban", "urban", "dense_urban")
    statistics = {
        combination: {
            scope: {region: fresh_stats() for region in ("overall", "los", "nlos")}
            for scope in scopes
        }
        for combination, _ in COMBINATIONS
    }
    map_counts: Counter[str] = Counter()

    with h5py.File(str(args.hdf5), "r") as handle:
        for number, reference in enumerate(test_refs, start=1):
            sample = hybrid_ref.load_hybrid_sample(handle, reference)
            target = sample["path_loss"]
            valid = sample["valid"]
            los = valid & (sample["los_mask"] > 0)
            nlos = valid & (sample["los_mask"] == 0)
            topology = hybrid_ref.sample_city_type(sample["topology"])
            map_counts[topology] += 1

            height = reference.uav_height_m
            antenna_bin = hybrid_ref.ant_bin(height)
            regime = hybrid_ref.regime_key(topology, "NLoS", antenna_bin)
            cost231 = compute_cost231_map(height, hybrid_ref)
            features = hybrid_ref.compute_pixel_features(
                sample["topology"], sample["los_mask"], cost231, height
            )
            nlos_prediction = linear_nlos_map(
                features, regime_coefficients[regime], hybrid_ref
            )
            los_with_rho_phi = los_model.predict_two_ray_map(
                height, two_ray_calibration
            )
            los_without_rho_phi = los_model.predict_radial_map(
                height, radial_calibration
            )
            los_flag = sample["los_mask"] > 0

            for combination, use_rho_phi in COMBINATIONS:
                los_prediction = (
                    los_with_rho_phi if use_rho_phi else los_without_rho_phi
                )
                prediction = np.where(
                    los_flag, los_prediction, nlos_prediction
                ).astype(np.float32)
                for scope in ("global", topology):
                    add_error(statistics[combination][scope]["overall"], prediction, target, valid)
                    add_error(statistics[combination][scope]["los"], prediction, target, los)
                    add_error(statistics[combination][scope]["nlos"], prediction, target, nlos)

            if number % max(args.log_every, 1) == 0 or number == len(test_refs):
                print(f"evaluate test [{number}/{len(test_refs)}]", flush=True)

    rows = []
    for combination, use_rho_phi in COMBINATIONS:
        for scope in scopes:
            bundle = statistics[combination][scope]
            rows.append(
                {
                    "combination": combination,
                    "rho_phi": "with" if use_rho_phi else "without",
                    "scope": scope,
                    "maps": len(test_refs) if scope == "global" else map_counts[scope],
                    "overall_rmse_db": rmse(bundle["overall"]),
                    "los_rmse_db": rmse(bundle["los"]),
                    "nlos_rmse_db": rmse(bundle["nlos"]),
                    "overall_pixels": int(bundle["overall"]["n"]),
                    "los_pixels": int(bundle["los"]["n"]),
                    "nlos_pixels": int(bundle["nlos"]["n"]),
                }
            )

    expected = {
        "with_rho_phi": 1.928749619998359,
        "without_rho_phi": 3.7292385336740956,
    }
    for combination, expected_rmse in expected.items():
        observed = next(
            float(row["overall_rmse_db"])
            for row in rows
            if row["combination"] == combination and row["scope"] == "global"
        )
        if not math.isclose(observed, expected_rmse, rel_tol=0.0, abs_tol=1e-9):
            raise RuntimeError(
                f"reproduction check failed for {combination}: {observed} != {expected_rmse}"
            )

    write_csv(args.out_dir / "rho_phi_rmse.csv", rows)
    write_markdown(args.out_dir / "rho_phi_rmse.md", rows)
    metadata = {
        "split": {
            "source": "Try 74/75 compatible split_city_holdout_try80",
            "split_seed": args.split_seed,
            "train_maps": len(train_refs),
            "validation_maps": len(validation_refs),
            "test_maps": len(test_refs),
        },
        "ablation_contract": {
            "rho_phi_with": "coherent two-ray rho, phi, and bias plus refitted radial residual",
            "rho_phi_without": "FSPL plus radial residual refitted after removing rho, phi, and two-ray bias",
            "itu_topology": "fixed to three topology-specific NLoS ridge calibrations with per-sample routing",
            "radial_r": "present and recalibrated in every combination",
            "building_pixels": "excluded from every metric",
        },
        "topology_map_counts": dict(sorted(map_counts.items())),
        "reproduction_checks": expected,
    }
    (args.out_dir / "rho_phi_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(rows, indent=2), flush=True)


if __name__ == "__main__":
    main()
