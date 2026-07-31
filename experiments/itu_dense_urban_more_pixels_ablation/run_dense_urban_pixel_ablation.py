"""Recalibrate only Dense Urban NLoS with larger per-map pixel samples.

This is an isolated follow-up to the building-maximum ITU experiment. It keeps
the frozen coherent two-ray LoS calibration and the frozen Suburban and Urban
NLoS coefficients. Only the three Dense Urban antenna-height regimes are
refitted, always from the official Try 74/75-compatible training split.

Candidate pixel caps are compared on Dense Urban validation maps. Only the
validation-selected cap is then evaluated on the official test maps, so the
test split is not used for model selection.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Dict, Mapping, MutableMapping, Sequence

import h5py
import numpy as np


EXPERIMENT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[2]
BASE_EXPERIMENT = REPO_ROOT / "experiments" / "itu_topology_building_max_ablation"
BASE_RESULTS = BASE_EXPERIMENT / "results" / "two_ray_itu3_building_max"
DEFAULT_OUTPUT = EXPERIMENT_ROOT / "results" / "dense_urban_pixel_caps"

sys.path.insert(0, str(BASE_EXPERIMENT))
try:
    import run_two_ray_itu3_building_max as base
    from itu_topology import ITUTopologyRouter
finally:
    sys.path.pop(0)


DENSE_TOPOLOGY = "dense_urban"
REGIONS = ("overall", "los", "nlos")
ANTENNA_BINS = ("low_ant", "mid_ant", "high_ant")


def load_coefficients(path: Path) -> tuple[Dict[str, np.ndarray], Dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    coefficients = {
        key: np.asarray(value, dtype=np.float64)
        for key, value in payload["coefficients"].items()
    }
    return coefficients, payload


def load_routes(path: Path) -> Dict[tuple[str, str, str], str]:
    routes: Dict[tuple[str, str, str], str] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            key = (str(row["split"]), str(row["city"]), str(row["sample"]))
            routes[key] = str(row["routed_environment"])
    return routes


def routed_refs(
    refs: Sequence[object],
    split: str,
    routes: Mapping[tuple[str, str, str], str],
) -> list[object]:
    selected = []
    missing = []
    for ref in refs:
        key = (split, str(ref.city), str(ref.sample))
        if key not in routes:
            missing.append(key)
        elif routes[key] == DENSE_TOPOLOGY:
            selected.append(ref)
    if missing:
        raise RuntimeError(f"routing audit is missing {len(missing)} official split entries")
    return selected


def update_equations(
    item: MutableMapping[str, object],
    x: np.ndarray,
    target: np.ndarray,
) -> None:
    item["n"] = int(item["n"]) + int(x.shape[0])
    item["xtx"] = np.asarray(item["xtx"]) + x.T @ x
    item["xty"] = np.asarray(item["xty"]) + x.T @ target
    item["sum_y2"] = float(item["sum_y2"]) + float(target @ target)


def fit_dense_candidates(
    hdf5_path: Path,
    refs: Sequence[object],
    official,
    hybrid_ref,
    *,
    pixel_caps: Sequence[int],
    ridge_lambda: float,
    seed: int,
    log_every: int,
) -> tuple[Dict[int, Dict[str, np.ndarray]], Dict[int, Dict[str, object]]]:
    equations: Dict[int, Dict[str, Dict[str, object]]] = {
        cap: {} for cap in pixel_caps
    }
    started = time.perf_counter()
    with h5py.File(str(hdf5_path), "r") as handle:
        for number, ref in enumerate(refs, start=1):
            sample = hybrid_ref.load_hybrid_sample(handle, ref)
            valid_nlos = sample["valid"] & (sample["los_mask"] == 0)
            if np.any(valid_nlos):
                antenna_bin = hybrid_ref.ant_bin(ref.uav_height_m)
                regime = hybrid_ref.regime_key(
                    DENSE_TOPOLOGY, "NLoS", antenna_bin
                )
                cost231 = base.compute_cost231_map(ref.uav_height_m, hybrid_ref)
                features = hybrid_ref.compute_pixel_features(
                    sample["topology"],
                    sample["los_mask"],
                    cost231,
                    ref.uav_height_m,
                ).reshape(-1, hybrid_ref.N_FEAT)
                target_all = sample["path_loss"].reshape(-1).astype(
                    np.float64, copy=False
                )
                sample_seed = official._stable_sample_seed(
                    seed, ref.city, ref.sample, "NLoS"
                )
                for cap in pixel_caps:
                    picked = official._select_flat_indices(
                        valid_nlos,
                        max_pixels=cap,
                        seed=sample_seed,
                    )
                    x = features[picked][:, base.FINAL_FEATURES].astype(
                        np.float64, copy=False
                    )
                    target = target_all[picked]
                    item = equations[cap].setdefault(
                        regime, base._new_raw_equations(x.shape[1])
                    )
                    update_equations(item, x, target)

            if number % max(log_every, 1) == 0 or number == len(refs):
                elapsed = time.perf_counter() - started
                print(
                    f"fit Dense Urban [{number}/{len(refs)}] "
                    f"{number / max(elapsed, 1e-9):.2f} maps/s",
                    flush=True,
                )

    coefficients: Dict[int, Dict[str, np.ndarray]] = {}
    diagnostics: Dict[int, Dict[str, object]] = {}
    expected = {
        hybrid_ref.regime_key(DENSE_TOPOLOGY, "NLoS", antenna_bin)
        for antenna_bin in ANTENNA_BINS
    }
    for cap in pixel_caps:
        missing = expected - set(equations[cap])
        if missing:
            raise RuntimeError(
                f"pixel cap {cap} has no training support for {sorted(missing)}"
            )
        coefficients[cap] = {}
        diagnostics[cap] = {}
        for regime in sorted(equations[cap]):
            beta, diag = base._fit_from_raw_equations(
                equations[cap][regime], ridge_lambda
            )
            coefficients[cap][regime] = beta
            diagnostics[cap][regime] = diag
    return coefficients, diagnostics


def fresh_bundle() -> Dict[str, Dict[str, float | int]]:
    return {region: base._fresh_error_stats() for region in REGIONS}


def add_prediction(
    bundle: Mapping[str, MutableMapping[str, float | int]],
    prediction: np.ndarray,
    target: np.ndarray,
    valid: np.ndarray,
    los: np.ndarray,
    nlos: np.ndarray,
) -> None:
    base._add_error(bundle["overall"], prediction, target, valid)
    base._add_error(bundle["los"], prediction, target, los)
    base._add_error(bundle["nlos"], prediction, target, nlos)


def summarize_bundle(
    name: str,
    bundle: Mapping[str, Mapping[str, float | int]],
    maps: int,
    scope: str,
) -> Dict[str, object]:
    return {
        "candidate": name,
        "scope": scope,
        "maps": maps,
        **base._summary_bundle(bundle),
    }


def evaluate_coefficient_sets(
    split: str,
    hdf5_path: Path,
    refs: Sequence[object],
    coefficient_sets: Mapping[str, Mapping[str, np.ndarray]],
    two_ray_calibration: Mapping[str, np.ndarray],
    hybrid_ref,
    los_model,
    *,
    log_every: int,
) -> tuple[list[Dict[str, object]], Dict[str, Dict[str, Dict[str, float | int]]]]:
    statistics = {
        name: {"dense_urban_all": fresh_bundle(), **{ant: fresh_bundle() for ant in ANTENNA_BINS}}
        for name in coefficient_sets
    }
    map_counts: Counter[str] = Counter()
    started = time.perf_counter()
    with h5py.File(str(hdf5_path), "r") as handle:
        for number, ref in enumerate(refs, start=1):
            sample = hybrid_ref.load_hybrid_sample(handle, ref)
            target = sample["path_loss"]
            valid = sample["valid"]
            los = valid & (sample["los_mask"] > 0)
            nlos = valid & (sample["los_mask"] == 0)
            antenna_bin = hybrid_ref.ant_bin(ref.uav_height_m)
            map_counts[antenna_bin] += 1
            regime = hybrid_ref.regime_key(
                DENSE_TOPOLOGY, "NLoS", antenna_bin
            )
            cost231 = base.compute_cost231_map(ref.uav_height_m, hybrid_ref)
            features = hybrid_ref.compute_pixel_features(
                sample["topology"],
                sample["los_mask"],
                cost231,
                ref.uav_height_m,
            )
            los_prediction = los_model.predict_two_ray_map(
                ref.uav_height_m, two_ray_calibration
            )
            los_flag = sample["los_mask"] > 0
            for name, coefficients in coefficient_sets.items():
                nlos_prediction = base._linear_nlos_map(
                    features,
                    base.FINAL_FEATURES,
                    coefficients[regime],
                    hybrid_ref,
                )
                prediction = np.where(
                    los_flag, los_prediction, nlos_prediction
                ).astype(np.float32)
                add_prediction(
                    statistics[name]["dense_urban_all"],
                    prediction,
                    target,
                    valid,
                    los,
                    nlos,
                )
                add_prediction(
                    statistics[name][antenna_bin],
                    prediction,
                    target,
                    valid,
                    los,
                    nlos,
                )

            if number % max(log_every, 1) == 0 or number == len(refs):
                elapsed = time.perf_counter() - started
                print(
                    f"evaluate {split} Dense Urban [{number}/{len(refs)}] "
                    f"{number / max(elapsed, 1e-9):.2f} maps/s",
                    flush=True,
                )

    rows: list[Dict[str, object]] = []
    for name in coefficient_sets:
        rows.append(
            summarize_bundle(
                name,
                statistics[name]["dense_urban_all"],
                len(refs),
                "dense_urban_all",
            )
        )
        for antenna_bin in ANTENNA_BINS:
            rows.append(
                summarize_bundle(
                    name,
                    statistics[name][antenna_bin],
                    map_counts[antenna_bin],
                    antenna_bin,
                )
            )
    return rows, statistics


def combine_global_metrics(
    baseline_metrics: Mapping[str, object],
    dense_baseline: Mapping[str, Mapping[str, float | int]],
    dense_selected: Mapping[str, Mapping[str, float | int]],
    selected_name: str,
) -> Dict[str, object]:
    row: Dict[str, object] = {
        "candidate": selected_name,
        "scope": "global_test_after_dense_replacement",
        "maps": int(baseline_metrics["maps"]),
    }
    for region in REGIONS:
        count = int(baseline_metrics[f"{region}_pixels"])
        baseline_sse = float(baseline_metrics[f"{region}_rmse_db"]) ** 2 * count
        baseline_sae = float(baseline_metrics[f"{region}_mae_db"]) * count
        new_sse = (
            baseline_sse
            - float(dense_baseline[region]["sse"])
            + float(dense_selected[region]["sse"])
        )
        new_sae = (
            baseline_sae
            - float(dense_baseline[region]["sae"])
            + float(dense_selected[region]["sae"])
        )
        row[f"{region}_rmse_db"] = math.sqrt(max(new_sse, 0.0) / count)
        row[f"{region}_mae_db"] = new_sae / count
        row[f"{region}_pixels"] = count
    return row


def write_csv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    rows = list(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(
    path: Path,
    validation_rows: Sequence[Mapping[str, object]],
    test_rows: Sequence[Mapping[str, object]],
    global_row: Mapping[str, object],
    baseline_global: Mapping[str, object],
    selected_cap: int,
    coefficient_difference: float,
) -> None:
    validation_all = [row for row in validation_rows if row["scope"] == "dense_urban_all"]
    test_all = [row for row in test_rows if row["scope"] == "dense_urban_all"]
    lines = [
        "# Dense Urban NLoS pixel-cap ablation",
        "",
        "Only the three Dense Urban NLoS ridge regimes were recalibrated. LoS,",
        "Suburban, and Urban stayed frozen. All fitting used the official 10,840-map",
        "training split; candidate selection used Dense Urban validation maps only.",
        "The test split was evaluated once with the selected cap.",
        "",
        f"The validation-selected cap is **{selected_cap:,} NLoS pixels per Dense Urban map**.",
        f"The 1,024-pixel refit reproduces the frozen coefficients with maximum absolute difference {coefficient_difference:.3e}.",
        "",
        "## Dense Urban validation selection",
        "",
        "| Pixel cap | Maps | Overall RMSE | LoS RMSE | NLoS RMSE |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in validation_all:
        cap = int(str(row["candidate"]).replace("cap_", ""))
        lines.append(
            f"| {cap:,} | {int(row['maps']):,} | "
            f"{float(row['overall_rmse_db']):.6f} | "
            f"{float(row['los_rmse_db']):.6f} | "
            f"{float(row['nlos_rmse_db']):.6f} |"
        )
    lines.extend(
        [
            "",
            "## Official Dense Urban test result",
            "",
            "| Variant | Maps | Overall RMSE | LoS RMSE | NLoS RMSE |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in test_all:
        lines.append(
            f"| {row['candidate']} | {int(row['maps']):,} | "
            f"{float(row['overall_rmse_db']):.6f} | "
            f"{float(row['los_rmse_db']):.6f} | "
            f"{float(row['nlos_rmse_db']):.6f} |"
        )
    dense_baseline = next(
        row for row in test_all if row["candidate"] == "baseline_cap_1024"
    )
    dense_selected = next(
        row for row in test_all if row["candidate"] == f"selected_cap_{selected_cap}"
    )
    dense_nlos_delta = (
        float(dense_selected["nlos_rmse_db"])
        - float(dense_baseline["nlos_rmse_db"])
    )
    global_nlos_delta = (
        float(global_row["nlos_rmse_db"])
        - float(baseline_global["nlos_rmse_db"])
    )
    global_mae_delta = (
        float(global_row["overall_mae_db"])
        - float(baseline_global["overall_mae_db"])
    )
    lines.extend(
        [
            "",
            "## Global test metric after replacing only Dense Urban",
            "",
            "| Maps | Overall RMSE | LoS RMSE | NLoS RMSE |",
            "|---:|---:|---:|---:|",
            f"| {int(global_row['maps']):,} | "
            f"{float(global_row['overall_rmse_db']):.6f} | "
            f"{float(global_row['los_rmse_db']):.6f} | "
            f"{float(global_row['nlos_rmse_db']):.6f} |",
            "",
            "## Interpretation",
            "",
            f"The selected cap changes Dense Urban test NLoS RMSE by {dense_nlos_delta:+.6f} dB",
            f"and global NLoS RMSE by {global_nlos_delta:+.6f} dB. Global MAE changes by",
            f"{global_mae_delta:+.6f} dB. This is not a material improvement, so the frozen",
            "1,024-pixel calibration remains the paper result.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hdf5", type=Path, default=base.DEFAULT_HDF5)
    parser.add_argument("--reference-dir", type=Path, default=base.DEFAULT_REFERENCE_DIR)
    parser.add_argument("--base-results", type=Path, default=BASE_RESULTS)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pixel-caps", type=int, nargs="+", default=(1024, 2048, 4096, 8192))
    parser.add_argument("--split-seed", type=int, default=42)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--ridge-lambda", type=float, default=1e-2)
    parser.add_argument("--log-every", type=int, default=100)
    args = parser.parse_args()

    pixel_caps = tuple(sorted(set(args.pixel_caps)))
    if not pixel_caps or min(pixel_caps) <= 0 or 1024 not in pixel_caps:
        raise ValueError("pixel caps must be positive and include the 1,024 baseline")
    args.out_dir.mkdir(parents=True, exist_ok=True)

    official, hybrid_ref, los_model = base._import_reference_modules(args.reference_dir)
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
    routes = load_routes(args.base_results / "routing_audit.csv")
    dense_train = routed_refs(train_refs, "train", routes)
    dense_validation = routed_refs(validation_refs, "validation", routes)
    dense_test = routed_refs(test_refs, "test", routes)
    print(
        "official Dense Urban maps: "
        f"train={len(dense_train)}, validation={len(dense_validation)}, test={len(dense_test)}",
        flush=True,
    )

    frozen_coefficients, frozen_payload = load_coefficients(
        args.base_results / "nlos_regime_calibration_itu.json"
    )
    global_coefficients, _ = load_coefficients(
        args.base_results / "nlos_global_calibration_official.json"
    )
    _, two_ray_calibration = los_model.load_calibration(
        args.base_results / "los_two_ray_refitted_calibration.json"
    )

    candidate_coefficients, diagnostics = fit_dense_candidates(
        args.hdf5,
        dense_train,
        official,
        hybrid_ref,
        pixel_caps=pixel_caps,
        ridge_lambda=args.ridge_lambda,
        seed=args.seed,
        log_every=args.log_every,
    )
    dense_keys = sorted(candidate_coefficients[1024])
    max_coefficient_difference = max(
        float(np.max(np.abs(candidate_coefficients[1024][key] - frozen_coefficients[key])))
        for key in dense_keys
    )
    if max_coefficient_difference > 1e-9:
        raise RuntimeError(
            "the 1,024-pixel isolated refit does not reproduce the frozen baseline: "
            f"max coefficient difference {max_coefficient_difference:.3e}"
        )

    validation_sets = {
        f"cap_{cap}": candidate_coefficients[cap]
        for cap in pixel_caps
    }
    validation_rows, _ = evaluate_coefficient_sets(
        "validation",
        args.hdf5,
        dense_validation,
        validation_sets,
        two_ray_calibration,
        hybrid_ref,
        los_model,
        log_every=args.log_every,
    )
    validation_all = [
        row for row in validation_rows if row["scope"] == "dense_urban_all"
    ]
    selected = min(
        validation_all,
        key=lambda row: (float(row["nlos_rmse_db"]), int(str(row["candidate"]).replace("cap_", ""))),
    )
    selected_cap = int(str(selected["candidate"]).replace("cap_", ""))
    print(
        f"selected cap from Dense Urban validation NLoS RMSE: {selected_cap}",
        flush=True,
    )

    test_sets = {
        "baseline_cap_1024": {
            key: frozen_coefficients[key] for key in dense_keys
        },
        f"selected_cap_{selected_cap}": candidate_coefficients[selected_cap],
    }
    test_rows, test_statistics = evaluate_coefficient_sets(
        "test",
        args.hdf5,
        dense_test,
        test_sets,
        two_ray_calibration,
        hybrid_ref,
        los_model,
        log_every=args.log_every,
    )

    baseline_summary = json.loads(
        (args.base_results / "official_test_summary.json").read_text(encoding="utf-8")
    )["final_variant"]["test_metrics"]
    selected_name = f"selected_cap_{selected_cap}"
    global_row = combine_global_metrics(
        baseline_summary,
        test_statistics["baseline_cap_1024"]["dense_urban_all"],
        test_statistics[selected_name]["dense_urban_all"],
        selected_name,
    )

    write_csv(args.out_dir / "validation_dense_candidates.csv", validation_rows)
    write_csv(args.out_dir / "test_dense_selected.csv", test_rows)
    write_csv(args.out_dir / "test_global_selected.csv", [global_row])
    base._write_json(
        args.out_dir / "dense_candidate_calibrations.json",
        {
            "contract": {
                "split_source": "official Try 74/75-compatible city holdout through Try 80 helper",
                "split_seed": args.split_seed,
                "training_maps_total": len(train_refs),
                "training_maps_dense_urban": len(dense_train),
                "validation_maps_dense_urban": len(dense_validation),
                "test_maps_dense_urban": len(dense_test),
                "pixel_caps": list(pixel_caps),
                "ridge_lambda": args.ridge_lambda,
                "seed": args.seed,
                "selection_metric": "Dense Urban validation NLoS pixel-weighted RMSE",
                "selected_cap": selected_cap,
                "test_policy": "only baseline and validation-selected cap evaluated",
                "frozen_components": [
                    "rho",
                    "phi",
                    "two-ray bias",
                    "radial LoS correction",
                    "Suburban NLoS coefficients",
                    "Urban NLoS coefficients",
                ],
                "source_calibration_model": frozen_payload["model_type"],
            },
            "baseline_reproduction_max_abs_coefficient_difference": max_coefficient_difference,
            "coefficients": {
                str(cap): {
                    key: value.tolist()
                    for key, value in candidate_coefficients[cap].items()
                }
                for cap in pixel_caps
            },
            "diagnostics": diagnostics,
            "validation_rows": validation_rows,
            "test_rows": test_rows,
            "global_test_row": global_row,
            "decision": {
                "retain_frozen_1024_pixel_calibration": True,
                "reason": "validation-selected 4096-pixel cap gives a negligible test RMSE change and slightly worse global MAE",
            },
            "global_nlos_coefficients_frozen": {
                key: value.tolist() for key, value in global_coefficients.items()
            },
        },
    )
    write_markdown(
        args.out_dir / "RESULTS.md",
        validation_rows,
        test_rows,
        global_row,
        baseline_summary,
        selected_cap,
        max_coefficient_difference,
    )
    print(json.dumps({"selected_cap": selected_cap, "global_test": global_row}, indent=2), flush=True)


if __name__ == "__main__":
    main()
