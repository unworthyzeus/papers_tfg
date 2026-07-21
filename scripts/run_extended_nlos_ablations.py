"""Run training-only recalibrated component ablations for the Try 78 prior.

The experiment extends the frozen paper reproduction without changing the
paper. It removes individual and nested groups of NLoS features, recalibrates
every remaining model on training cities, and evaluates the fixed variants on
the official validation and test city splits.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, Mapping, MutableMapping, Sequence

import h5py
import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_ROOT = REPO_ROOT
TFG_ROOT = REPO_ROOT.parent / "TFGpractice"
HDF5_DEFAULT = TFG_ROOT / "Datasets" / "CKM_Dataset_270326.h5"
REFERENCE_DEFAULT = TFG_ROOT / "TFGEightiethTry80" / "scripts" / "recalibrate_priors"
LOS_CAL_DEFAULT = (
    TFG_ROOT
    / "TFGSeventyEighthTry78"
    / "hybrid_out_try80_split"
    / "calibrations"
    / "try78_los_two_ray_calibration_try80split.json"
)
OUTPUT_DEFAULT = (
    REPO_ROOT
    / "drafts"
    / "conference_attenuation_priors"
    / "data"
    / "official_split_analysis"
    / "extended_nlos_ablations"
)


FULL_FEATURE_NAMES = (
    "pl_c",
    "log1p_d2d",
    "density_15",
    "density_41",
    "height_15",
    "height_41",
    "density_41_x_logd",
    "nlos_15",
    "nlos_41",
    "nlos_41_x_logd",
    "shadow_sigma",
    "theta_norm",
    "nlos_41_x_theta",
    "bias",
)


def _keep_without(*removed: str) -> tuple[int, ...]:
    removed_set = set(removed)
    return tuple(i for i, name in enumerate(FULL_FEATURE_NAMES) if name not in removed_set)


def _keep_only(*retained: str) -> tuple[int, ...]:
    retained_set = set(retained)
    return tuple(i for i, name in enumerate(FULL_FEATURE_NAMES) if name in retained_set)


# All variants are fixed before validation/test evaluation.  The final bias
# feature is retained in every fit so that each ablation gets its own intercept.
NLOS_SPECS = {
    "full": {
        "label": "Complete NLoS model",
        "routing": "full_9_regimes",
        "keep": tuple(range(len(FULL_FEATURE_NAMES))),
    },
    "without_cost231": {
        "label": "Without COST231 term",
        "routing": "full_9_regimes",
        "keep": _keep_without("pl_c"),
    },
    "without_distance": {
        "label": "Without distance terms",
        "routing": "full_9_regimes",
        "keep": _keep_without("log1p_d2d", "density_41_x_logd", "nlos_41_x_logd"),
    },
    "without_building_density": {
        "label": "Without local building density",
        "routing": "full_9_regimes",
        "keep": _keep_without("density_15", "density_41", "density_41_x_logd"),
    },
    "without_building_height": {
        "label": "Without local building height",
        "routing": "full_9_regimes",
        "keep": _keep_without("height_15", "height_41"),
    },
    "without_local_visibility": {
        "label": "Without local NLoS fractions",
        "routing": "full_9_regimes",
        "keep": _keep_without("nlos_15", "nlos_41", "nlos_41_x_logd", "nlos_41_x_theta"),
    },
    "without_shadow_sigma": {
        "label": "Without shadowing spread proxy",
        "routing": "full_9_regimes",
        "keep": _keep_without("shadow_sigma"),
    },
    "without_elevation": {
        "label": "Without elevation terms",
        "routing": "full_9_regimes",
        "keep": _keep_without("theta_norm", "nlos_41_x_theta"),
    },
    "without_interactions": {
        "label": "Without interaction terms",
        "routing": "full_9_regimes",
        "keep": _keep_without("density_41_x_logd", "nlos_41_x_logd", "nlos_41_x_theta"),
    },
    "without_local_morphology": {
        "label": "Without all local morphology and visibility",
        "routing": "full_9_regimes",
        "keep": _keep_without(
            "density_15",
            "density_41",
            "height_15",
            "height_41",
            "density_41_x_logd",
            "nlos_15",
            "nlos_41",
            "nlos_41_x_logd",
            "nlos_41_x_theta",
        ),
    },
    "topology_only_routing": {
        "label": "Without transmitter-height routing",
        "routing": "topology_only",
        "keep": tuple(range(len(FULL_FEATURE_NAMES))),
    },
    "height_only_routing": {
        "label": "Without topology routing",
        "routing": "height_only",
        "keep": tuple(range(len(FULL_FEATURE_NAMES))),
    },
    "global_routing": {
        "label": "Without topology and height routing",
        "routing": "global",
        "keep": tuple(range(len(FULL_FEATURE_NAMES))),
    },
    "without_15m_scale": {
        "label": "Without the 15-pixel local scale",
        "routing": "full_9_regimes",
        "keep": _keep_without("density_15", "height_15", "nlos_15"),
    },
    "without_41m_scale": {
        "label": "Without the 41-pixel local scale",
        "routing": "full_9_regimes",
        "keep": _keep_without(
            "density_41",
            "height_41",
            "density_41_x_logd",
            "nlos_41",
            "nlos_41_x_logd",
            "nlos_41_x_theta",
        ),
    },
    "single_41m_scale": {
        "label": "Only 41-pixel morphology plus geometry",
        "routing": "full_9_regimes",
        "keep": _keep_only(
            "pl_c",
            "log1p_d2d",
            "density_41",
            "height_41",
            "nlos_41",
            "shadow_sigma",
            "theta_norm",
            "bias",
        ),
    },
    "lean_six_topology": {
        "label": "Six-feature topology-routed model",
        "routing": "topology_only",
        "keep": _keep_only(
            "log1p_d2d", "density_15", "density_41", "nlos_15", "nlos_41", "bias"
        ),
    },
    "lean_four_full_routing": {
        "label": "Four-feature model with nine regimes",
        "routing": "full_9_regimes",
        "keep": _keep_only("log1p_d2d", "density_41", "nlos_41", "bias"),
    },
    "lean_four_topology": {
        "label": "Four-feature topology-routed model",
        "routing": "topology_only",
        "keep": _keep_only("log1p_d2d", "density_41", "nlos_41", "bias"),
    },
    "distance_density_topology": {
        "label": "Distance and density only, topology-routed",
        "routing": "topology_only",
        "keep": _keep_only("log1p_d2d", "density_41", "bias"),
    },
    "distance_visibility_topology": {
        "label": "Distance and local visibility only, topology-routed",
        "routing": "topology_only",
        "keep": _keep_only("log1p_d2d", "nlos_41", "bias"),
    },
    "distance_only_full_routing": {
        "label": "Distance only with nine regimes",
        "routing": "full_9_regimes",
        "keep": _keep_only("log1p_d2d", "bias"),
    },
    "distance_only_topology": {
        "label": "Distance only, topology-routed",
        "routing": "topology_only",
        "keep": _keep_only("log1p_d2d", "bias"),
    },
    "cost231_only_full_routing": {
        "label": "Calibrated COST231 only with nine regimes",
        "routing": "full_9_regimes",
        "keep": _keep_only("pl_c", "bias"),
    },
    "cost231_only_topology": {
        "label": "Calibrated COST231 only, topology-routed",
        "routing": "topology_only",
        "keep": _keep_only("pl_c", "bias"),
    },
    "constant_full_routing": {
        "label": "Constant prediction in each of nine regimes",
        "routing": "full_9_regimes",
        "keep": _keep_only("bias"),
    },
    "constant_topology": {
        "label": "Constant prediction per topology",
        "routing": "topology_only",
        "keep": _keep_only("bias"),
    },
    "constant_global": {
        "label": "Single global NLoS constant",
        "routing": "global",
        "keep": _keep_only("bias"),
    },
}

LOS_SPECS = {
    "full": "Coherent two-ray plus radial residual",
    "without_radial": "Without radial residual",
    "without_coherent": "Without coherent two-ray term",
    "fspl_bias_only": "FSPL plus height-binned bias only",
}


def _write_csv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    rows = list(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else [])
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def _portable_path(path: Path) -> str:
    resolved = path.resolve()
    workspace = REPO_ROOT.parent.resolve()
    if resolved.is_relative_to(workspace):
        return resolved.relative_to(workspace).as_posix()
    return str(resolved)


def _new_equations(p: int) -> Dict[str, object]:
    return {
        "n": 0,
        "xtx": np.zeros((p, p), dtype=np.float64),
        "xty": np.zeros(p, dtype=np.float64),
        "sum_y2": 0.0,
    }


def _add_equations(item: MutableMapping[str, object], x: np.ndarray, y: np.ndarray) -> None:
    item["n"] = int(item["n"]) + int(x.shape[0])
    item["xtx"] = np.asarray(item["xtx"]) + x.T @ x
    item["xty"] = np.asarray(item["xty"]) + x.T @ y
    item["sum_y2"] = float(item["sum_y2"]) + float(y @ y)


def _routing_key(routing: str, city_type: str, antenna_bin: str, hybrid_ref) -> str:
    if routing == "full_9_regimes":
        return hybrid_ref.regime_key(city_type, "NLoS", antenna_bin)
    if routing == "topology_only":
        return city_type
    if routing == "height_only":
        return antenna_bin
    if routing == "global":
        return "all"
    raise KeyError(routing)


def fit_all(
    hdf5_path: Path,
    refs: Sequence[object],
    official,
    hybrid_ref,
    los_model,
    base,
    two_ray_calibration: Mapping[str, np.ndarray],
    *,
    max_pixels: int,
    ridge_lambda: float,
    seed: int,
    log_every: int,
) -> tuple[Dict[str, Dict[str, np.ndarray]], Dict[str, object], Dict[str, np.ndarray]]:
    p = len(FULL_FEATURE_NAMES)
    equations = {routing: {} for routing in {str(v["routing"]) for v in NLOS_SPECS.values()}}
    height_bins = np.asarray(two_ray_calibration["height_bins_m"], dtype=np.float64)
    bias_sum = defaultdict(float)
    bias_count = defaultdict(int)
    started = time.perf_counter()

    with h5py.File(str(hdf5_path), "r") as handle:
        for number, ref in enumerate(refs, start=1):
            sample = hybrid_ref.load_hybrid_sample(handle, ref)
            city_type = hybrid_ref.sample_city_type(sample["topology"])
            antenna_bin = hybrid_ref.ant_bin(ref.uav_height_m)

            valid_nlos = sample["valid"] & (sample["los_mask"] == 0)
            if np.any(valid_nlos):
                prior = base.compute_cost231_map(ref.uav_height_m, hybrid_ref)
                features = hybrid_ref.compute_pixel_features(
                    sample["topology"], sample["los_mask"], prior, ref.uav_height_m
                )[..., base.FINAL_FEATURES].reshape(-1, p)
                picked = official._select_flat_indices(
                    valid_nlos,
                    max_pixels=max_pixels,
                    seed=official._stable_sample_seed(seed, ref.city, ref.sample, "NLoS"),
                )
                x = features[picked].astype(np.float64, copy=False)
                y = sample["path_loss"].reshape(-1)[picked].astype(np.float64, copy=False)
                for routing, grouped in equations.items():
                    key = _routing_key(routing, city_type, antenna_bin, hybrid_ref)
                    _add_equations(grouped.setdefault(key, _new_equations(p)), x, y)

            valid_los = sample["valid"] & (sample["los_mask"] > 0)
            if np.any(valid_los):
                picked_los = official._select_flat_indices(
                    valid_los,
                    max_pixels=max_pixels,
                    seed=official._stable_sample_seed(seed + 7919, ref.city, ref.sample, "LoS"),
                )
                residual = (
                    sample["path_loss"].reshape(-1)[picked_los].astype(np.float64)
                    - los_model.fspl_db(ref.uav_height_m).reshape(-1)[picked_los].astype(np.float64)
                )
                bin_key = float(los_model.height_bin_key(ref.uav_height_m, 5.0))
                bias_sum[bin_key] += float(residual.sum())
                bias_count[bin_key] += int(residual.size)

            if number % max(log_every, 1) == 0 or number == len(refs):
                elapsed = time.perf_counter() - started
                print(
                    f"fit [{number}/{len(refs)}] {number / max(elapsed, 1e-9):.2f} maps/s",
                    flush=True,
                )

    coefs: Dict[str, Dict[str, np.ndarray]] = {}
    diagnostics: Dict[str, object] = {}
    for variant, spec in NLOS_SPECS.items():
        routing = str(spec["routing"])
        keep = np.asarray(spec["keep"], dtype=np.int64)
        coefs[variant] = {}
        diagnostics[variant] = {}
        for key, full_item in sorted(equations[routing].items()):
            sub_item = {
                "n": int(full_item["n"]),
                "xtx": np.asarray(full_item["xtx"])[np.ix_(keep, keep)],
                "xty": np.asarray(full_item["xty"])[keep],
                "sum_y2": float(full_item["sum_y2"]),
            }
            beta, diag = base._fit_from_raw_equations(sub_item, ridge_lambda)
            coefs[variant][key] = beta
            diagnostics[variant][key] = diag

    bias_values = np.asarray(
        [bias_sum.get(float(h), 0.0) / max(bias_count.get(float(h), 0), 1) for h in height_bins],
        dtype=np.float32,
    )
    bias_calibration = {
        "height_bins_m": height_bins.astype(np.float32),
        "bias_db": bias_values,
        "fit_count": np.asarray([bias_count.get(float(h), 0) for h in height_bins], dtype=np.int64),
    }
    return coefs, diagnostics, bias_calibration


def _fresh_stats() -> Dict[str, float | int]:
    return {"sse": 0.0, "sae": 0.0, "n": 0}


def _add_vector_stats(stats: MutableMapping[str, float | int], error: np.ndarray) -> None:
    values = error.astype(np.float64, copy=False)
    stats["sse"] = float(stats["sse"]) + float(np.square(values).sum())
    stats["sae"] = float(stats["sae"]) + float(np.abs(values).sum())
    stats["n"] = int(stats["n"]) + int(values.size)


def _metrics(stats: Mapping[str, float | int]) -> tuple[float, float]:
    n = max(int(stats["n"]), 1)
    return math.sqrt(float(stats["sse"]) / n), float(stats["sae"]) / n


def evaluate(
    split: str,
    hdf5_path: Path,
    refs: Sequence[object],
    radial_calibration: Mapping[str, np.ndarray],
    two_ray_calibration: Mapping[str, np.ndarray],
    bias_calibration: Mapping[str, np.ndarray],
    coefs: Mapping[str, Mapping[str, np.ndarray]],
    hybrid_ref,
    los_model,
    base,
    *,
    log_every: int,
) -> list[Dict[str, object]]:
    los_stats = {variant: _fresh_stats() for variant in LOS_SPECS}
    nlos_stats = {variant: _fresh_stats() for variant in NLOS_SPECS}
    started = time.perf_counter()

    with h5py.File(str(hdf5_path), "r") as handle:
        for number, ref in enumerate(refs, start=1):
            sample = hybrid_ref.load_hybrid_sample(handle, ref)
            target = sample["path_loss"]
            city_type = hybrid_ref.sample_city_type(sample["topology"])
            antenna_bin = hybrid_ref.ant_bin(ref.uav_height_m)

            los_mask = sample["valid"] & (sample["los_mask"] > 0)
            if np.any(los_mask):
                bias = los_model._interpolate_scalar(
                    ref.uav_height_m,
                    bias_calibration["height_bins_m"],
                    bias_calibration["bias_db"],
                )
                los_predictions = {
                    "full": los_model.predict_two_ray_map(ref.uav_height_m, two_ray_calibration),
                    "without_radial": base._two_ray_without_radial(
                        ref.uav_height_m, two_ray_calibration, los_model
                    ),
                    "without_coherent": los_model.predict_radial_map(
                        ref.uav_height_m, radial_calibration
                    ),
                    "fspl_bias_only": np.clip(
                        los_model.fspl_db(ref.uav_height_m) + bias,
                        los_model.PATH_LOSS_MIN_DB,
                        los_model.PATH_LOSS_MAX_DB,
                    ),
                }
                for variant, pred in los_predictions.items():
                    _add_vector_stats(los_stats[variant], pred[los_mask] - target[los_mask])

            nlos_mask = sample["valid"] & (sample["los_mask"] == 0)
            if np.any(nlos_mask):
                prior = base.compute_cost231_map(ref.uav_height_m, hybrid_ref)
                features = hybrid_ref.compute_pixel_features(
                    sample["topology"], sample["los_mask"], prior, ref.uav_height_m
                )[..., base.FINAL_FEATURES]
                x = features[nlos_mask].astype(np.float64, copy=False)
                beta_matrix = np.zeros((len(FULL_FEATURE_NAMES), len(NLOS_SPECS)), dtype=np.float64)
                for column, (variant, spec) in enumerate(NLOS_SPECS.items()):
                    key = _routing_key(str(spec["routing"]), city_type, antenna_bin, hybrid_ref)
                    keep = np.asarray(spec["keep"], dtype=np.int64)
                    beta_matrix[keep, column] = coefs[variant][key]
                pred = np.clip(
                    x @ beta_matrix,
                    hybrid_ref.PATH_LOSS_MIN_DB,
                    hybrid_ref.PATH_LOSS_MAX_DB,
                )
                error = pred - target[nlos_mask].astype(np.float64)[:, None]
                for column, variant in enumerate(NLOS_SPECS):
                    _add_vector_stats(nlos_stats[variant], error[:, column])

            if number % max(log_every, 1) == 0 or number == len(refs):
                elapsed = time.perf_counter() - started
                full_los = los_stats["full"]
                full_nlos = nlos_stats["full"]
                total_sse = float(full_los["sse"]) + float(full_nlos["sse"])
                total_n = int(full_los["n"]) + int(full_nlos["n"])
                print(
                    f"evaluate {split} [{number}/{len(refs)}] "
                    f"RMSE={math.sqrt(total_sse / max(total_n, 1)):.4f} dB, "
                    f"{number / max(elapsed, 1e-9):.2f} maps/s",
                    flush=True,
                )

    full_los = los_stats["full"]
    full_nlos = nlos_stats["full"]
    baseline_sse = float(full_los["sse"]) + float(full_nlos["sse"])
    baseline_n = int(full_los["n"]) + int(full_nlos["n"])
    baseline_rmse = math.sqrt(baseline_sse / baseline_n)
    rows: list[Dict[str, object]] = []

    def append_row(family: str, variant: str, label: str, ls, ns) -> None:
        los_rmse, los_mae = _metrics(ls)
        nlos_rmse, nlos_mae = _metrics(ns)
        n_total = int(ls["n"]) + int(ns["n"])
        sse_total = float(ls["sse"]) + float(ns["sse"])
        sae_total = float(ls["sae"]) + float(ns["sae"])
        overall_rmse = math.sqrt(sse_total / n_total)
        rows.append(
            {
                "split": split,
                "family": family,
                "variant": variant,
                "label": label,
                "overall_rmse_db": overall_rmse,
                "delta_overall_rmse_db": overall_rmse - baseline_rmse,
                "overall_mae_db": sae_total / n_total,
                "los_rmse_db": los_rmse,
                "los_mae_db": los_mae,
                "los_pixels": int(ls["n"]),
                "nlos_rmse_db": nlos_rmse,
                "nlos_mae_db": nlos_mae,
                "nlos_pixels": int(ns["n"]),
            }
        )

    append_row("baseline", "full", "Complete recalibrated prior", full_los, full_nlos)
    for variant, spec in NLOS_SPECS.items():
        if variant != "full":
            append_row("NLoS", variant, str(spec["label"]), full_los, nlos_stats[variant])
    for variant, label in LOS_SPECS.items():
        if variant != "full":
            append_row("LoS", variant, label, los_stats[variant], full_nlos)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hdf5", type=Path, default=HDF5_DEFAULT)
    parser.add_argument("--reference-dir", type=Path, default=REFERENCE_DEFAULT)
    parser.add_argument("--los-calibration", type=Path, default=LOS_CAL_DEFAULT)
    parser.add_argument("--out-dir", type=Path, default=OUTPUT_DEFAULT)
    parser.add_argument("--split-seed", type=int, default=42)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--ridge-lambda", type=float, default=1e-2)
    parser.add_argument("--pixels-per-map", type=int, default=1024)
    parser.add_argument("--log-every", type=int, default=250)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    import importlib.util

    script_path = PAPER_ROOT / "scripts" / "run_conference_attenuation_ablation.py"
    spec = importlib.util.spec_from_file_location("paper_ablation", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {script_path}")
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    official, hybrid_ref, los_model = base._import_reference_modules(args.reference_dir)

    refs = los_model.enumerate_samples(args.hdf5)
    train_refs, val_refs, test_refs = official.split_city_holdout_try80(
        refs, val_ratio=0.15, test_ratio=0.15, split_seed=args.split_seed
    )
    print(
        f"official split: train={len(train_refs)}, val={len(val_refs)}, test={len(test_refs)}",
        flush=True,
    )
    radial_calibration, two_ray_calibration = los_model.load_calibration(args.los_calibration)
    coefs, diagnostics, bias_calibration = fit_all(
        args.hdf5,
        train_refs,
        official,
        hybrid_ref,
        los_model,
        base,
        two_ray_calibration,
        max_pixels=args.pixels_per_map,
        ridge_lambda=args.ridge_lambda,
        seed=args.seed,
        log_every=args.log_every,
    )

    calibration_payload = {
        "contract": {
            "split": "Try 74/75 compatible Try 80 city holdout",
            "split_seed": args.split_seed,
            "training_maps": len(train_refs),
            "training_cities": sorted({r.city for r in train_refs}),
            "pixels_per_map": args.pixels_per_map,
            "ridge_lambda": args.ridge_lambda,
            "seed": args.seed,
            "building_pixels": "excluded before fitting and evaluation",
        },
        "feature_names": list(FULL_FEATURE_NAMES),
        "variants": {
            variant: {
                "label": spec["label"],
                "routing": spec["routing"],
                "kept_features": [FULL_FEATURE_NAMES[i] for i in spec["keep"]],
                "coefficients": {key: value.tolist() for key, value in coefs[variant].items()},
                "diagnostics": diagnostics[variant],
            }
            for variant, spec in NLOS_SPECS.items()
        },
        "fspl_bias_calibration": {key: value.tolist() for key, value in bias_calibration.items()},
        "los_calibration_source": _portable_path(args.los_calibration),
    }
    _write_json(args.out_dir / "recalibrated_models.json", calibration_payload)

    val_rows = evaluate(
        "validation",
        args.hdf5,
        val_refs,
        radial_calibration,
        two_ray_calibration,
        bias_calibration,
        coefs,
        hybrid_ref,
        los_model,
        base,
        log_every=args.log_every,
    )
    test_rows = evaluate(
        "test",
        args.hdf5,
        test_refs,
        radial_calibration,
        two_ray_calibration,
        bias_calibration,
        coefs,
        hybrid_ref,
        los_model,
        base,
        log_every=args.log_every,
    )
    rows = val_rows + test_rows
    _write_csv(args.out_dir / "component_ablation_metrics.csv", rows)
    _write_json(
        args.out_dir / "summary.json",
        {
            "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "contract": calibration_payload["contract"],
            "rows": rows,
        },
    )
    print(json.dumps({"output": str(args.out_dir), "rows": rows}, indent=2), flush=True)


if __name__ == "__main__":
    main()
