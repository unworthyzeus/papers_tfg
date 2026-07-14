"""Audit the frozen Try-78 attenuation prior on the final Try-80 test cities.

The script uses the implementation functions from Final_Code_TFG so the paper
tables describe the deployed formulas rather than a reimplementation. It emits
the exact per-regime coefficients and pixel-weighted mean feature/contribution
statistics for NLoS receivers. It also recomputes the headline attenuation
metrics and the valid-pixel-weighted per-map correlation.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import h5py
import numpy as np


TEST_CITIES = (
    "Barcelona", "Beijing", "Carcassonne", "Copenhagen", "Halifax",
    "Jaipur", "Johannesburg", "Key West", "Kuala Lumpur", "Osaka",
    "Phuket", "Pune", "Surat", "Vancouver",
)
REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("try80_priors_for_audit", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def add_group(stats, group: str, features: np.ndarray, coef: np.ndarray) -> None:
    n = int(features.shape[0])
    if n == 0:
        return
    s = np.sum(features, axis=0, dtype=np.float64)
    rec = stats[group]
    rec["count"] += n
    rec["feature_sum"] += s
    rec["coef_weighted_sum"] += n * coef
    rec["contribution_sum"] += s * coef
    rec["abs_contribution_sum"] += np.sum(np.abs(features), axis=0, dtype=np.float64) * np.abs(coef)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--hdf5", type=Path,
        default=Path(r"C:\TFG\TFGAllProgress_Tries_and_Attempts\Datasets\CKM_Dataset_270326.h5"),
    )
    parser.add_argument(
        "--prior-module", type=Path,
        default=Path(r"C:\TFG\Final_Code_TFG\TFGEightiethTry80_preliminary_code\src\priors_try80.py"),
    )
    parser.add_argument(
        "--los-calibration", type=Path,
        default=Path(r"C:\TFG\Final_Code_TFG\TFGEightiethTry80_preliminary_code\calibrations\try78_los_two_ray_calibration.json"),
    )
    parser.add_argument(
        "--nlos-calibration", type=Path,
        default=REPO_ROOT / "drafts" / "conference_attenuation_priors" / "data" / "frozen_nlos_regime_calibration.json",
    )
    parser.add_argument(
        "--out-dir", type=Path,
        default=REPO_ROOT / "drafts" / "conference_attenuation_priors" / "data",
    )
    parser.add_argument("--max-maps", type=int, default=None)
    parser.add_argument(
        "--stride", type=int, default=1,
        help="Audit every Nth test map (deterministic, after city/sample sorting).",
    )
    parser.add_argument(
        "--terms-only", action="store_true",
        help="Skip prediction metrics and compute only the NLoS term audit.",
    )
    parser.add_argument("--log-every", type=int, default=100)
    args = parser.parse_args()

    priors = load_module(args.prior_module)
    calibration = json.loads(args.nlos_calibration.read_text(encoding="utf-8"))
    names = tuple(calibration["feature_names"])
    coefs = {key: np.asarray(value, dtype=np.float64)
             for key, value in calibration["coefficients"].items()}
    los_cal = None if args.terms_only else priors._load_try78_los_calibration(args.los_calibration)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    stats = defaultdict(lambda: {
        "count": 0,
        "feature_sum": np.zeros(len(names), dtype=np.float64),
        "coef_weighted_sum": np.zeros(len(names), dtype=np.float64),
        "contribution_sum": np.zeros(len(names), dtype=np.float64),
        "abs_contribution_sum": np.zeros(len(names), dtype=np.float64),
    })

    sse = 0.0
    sae = 0.0
    valid_count = 0
    los_sse = 0.0
    los_count = 0
    nlos_sse = 0.0
    nlos_count = 0
    corr_weighted_sum = 0.0
    corr_weight = 0
    map_count = 0

    with h5py.File(args.hdf5, "r") as handle:
        refs = [(city, sample) for city in TEST_CITIES for sample in sorted(handle[city].keys())]
        refs = refs[:: max(args.stride, 1)]
        if args.max_maps is not None:
            refs = refs[: args.max_maps]

        for index, (city, sample_name) in enumerate(refs, start=1):
            group = handle[city][sample_name]
            topology = np.asarray(group["topology_map"][...], dtype=np.float32)
            los_mask = np.asarray(group["los_mask"][...], dtype=np.float32)
            target = np.asarray(group["path_loss"][...], dtype=np.float32)
            h_tx = float(np.asarray(group["uav_height"][...]).reshape(-1)[0])

            raw_prior = priors._compute_formula_prior_78(los_mask, h_tx)
            features = priors._compute_pixel_features_78(topology, los_mask, raw_prior, h_tx)
            topology_class = priors._sample_city_type_78(topology)
            antenna_bin = priors.ant_bin(h_tx)
            key = f"{topology_class}|NLoS|{antenna_bin}"
            if key not in coefs:
                raise KeyError(f"No exact NLoS calibration for {key}")
            coef = coefs[key]

            ground = topology == 0.0
            valid = ground & np.isfinite(target) & (target >= priors.PATH_LOSS_MIN_DB)
            is_los = valid & (los_mask > 0.5)
            is_nlos = valid & (los_mask <= 0.5)

            nlos_features = features[is_nlos].astype(np.float64, copy=False)
            add_group(stats, "all", nlos_features, coef)
            add_group(stats, topology_class, nlos_features, coef)
            add_group(stats, key, nlos_features, coef)

            if not args.terms_only:
                los_pred = priors._predict_two_ray_map(h_tx, los_cal)
                nlos_pred = np.clip(features @ coef, priors.PATH_LOSS_MIN_DB, priors.PATH_LOSS_MAX_DB)
                prediction = np.where(los_mask > 0.5, los_pred, nlos_pred)

                error = prediction[valid].astype(np.float64) - target[valid].astype(np.float64)
                sse += float(error @ error)
                sae += float(np.sum(np.abs(error)))
                valid_count += int(error.size)

                error_los = prediction[is_los].astype(np.float64) - target[is_los].astype(np.float64)
                los_sse += float(error_los @ error_los)
                los_count += int(error_los.size)
                error_nlos = prediction[is_nlos].astype(np.float64) - target[is_nlos].astype(np.float64)
                nlos_sse += float(error_nlos @ error_nlos)
                nlos_count += int(error_nlos.size)

                pred_v = prediction[valid].astype(np.float64)
                target_v = target[valid].astype(np.float64)
                if pred_v.size >= 2:
                    pred_v -= pred_v.mean()
                    target_v -= target_v.mean()
                    denom = float(np.linalg.norm(pred_v) * np.linalg.norm(target_v))
                    if denom > 0.0:
                        corr_weighted_sum += pred_v.size * float((pred_v @ target_v) / denom)
                        corr_weight += int(pred_v.size)
            map_count += 1

            if index % args.log_every == 0 or index == len(refs):
                print(f"audited {index}/{len(refs)} maps", flush=True)

    exact_path = args.out_dir / "nlos_exact_coefficients.csv"
    with exact_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("regime", "topology_class", "antenna_bin", "feature", "coefficient"))
        for key in sorted(k for k in coefs if "|NLoS|" in k):
            topology_class, _, antenna_bin = key.split("|")
            for name, value in zip(names, coefs[key]):
                writer.writerow((key, topology_class, antenna_bin, name, f"{value:.12g}"))

    audit_path = args.out_dir / "nlos_test_term_audit.csv"
    with audit_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow((
            "group", "nlos_pixels", "feature", "mean_coefficient",
            "mean_feature_value", "mean_signed_contribution_db",
            "mean_absolute_contribution_db", "absolute_contribution_rank",
        ))
        for group_name in sorted(stats):
            rec = stats[group_name]
            n = rec["count"]
            mean_abs = rec["abs_contribution_sum"] / n
            ranks = np.empty(len(names), dtype=int)
            ranks[np.argsort(-mean_abs)] = np.arange(1, len(names) + 1)
            for i, name in enumerate(names):
                writer.writerow((
                    group_name, n, name,
                    f"{rec['coef_weighted_sum'][i] / n:.12g}",
                    f"{rec['feature_sum'][i] / n:.12g}",
                    f"{rec['contribution_sum'][i] / n:.12g}",
                    f"{mean_abs[i]:.12g}", int(ranks[i]),
                ))

    metrics = {
        "maps_audited": map_count,
        "test_map_stride": max(args.stride, 1),
        "terms_only": args.terms_only,
        "nlos_pixels_in_term_audit": stats["all"]["count"],
        "calibration_meta": calibration.get("meta", {}),
    }
    if not args.terms_only:
        metrics.update({
            "valid_pixels": valid_count,
            "los_pixels": los_count,
            "nlos_pixels": nlos_count,
            "rmse_db": math.sqrt(sse / valid_count),
            "mae_db": sae / valid_count,
            "los_rmse_db": math.sqrt(los_sse / los_count),
            "nlos_rmse_db": math.sqrt(nlos_sse / nlos_count),
            "map_correlation": corr_weighted_sum / corr_weight,
            "map_correlation_weight": corr_weight,
            "definition": "valid-pixel-weighted mean of per-map Pearson correlations",
        })
    (args.out_dir / "attenuation_audit_metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
