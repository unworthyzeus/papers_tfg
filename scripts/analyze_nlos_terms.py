"""Audit the frozen COST231 NLoS regression on the official final test split.

The script reads the current 14-feature, nine-regime calibration produced by
``run_conference_attenuation_ablation.py``. It exports exact coefficients and
pixel-weighted applied-term statistics. Building pixels and ground pixels
without a valid stored attenuation target are excluded.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, Mapping, MutableMapping, Sequence

import h5py
import numpy as np

from run_conference_attenuation_ablation import compute_cost231_map, final_feature_names


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TFG_ROOT = REPO_ROOT.parent
DEFAULT_HDF5 = DEFAULT_TFG_ROOT / "TFGpractice" / "Datasets" / "CKM_Dataset_270326.h5"
DEFAULT_REFERENCE_DIR = (
    DEFAULT_TFG_ROOT
    / "TFGpractice"
    / "TFGEightiethTry80"
    / "scripts"
    / "recalibrate_priors"
)
DEFAULT_ANALYSIS_DIR = (
    REPO_ROOT
    / "drafts"
    / "conference_attenuation_priors"
    / "data"
    / "official_split_analysis"
)
DEFAULT_CALIBRATION = DEFAULT_ANALYSIS_DIR / "nlos_regime_calibration_official.json"
FEATURE_INDICES = tuple(range(1, 15))


def _import_reference_modules(reference_dir: Path):
    sys.path.insert(0, str(reference_dir))
    try:
        import run_try78_on_try80_split as official
        import try78_hybrid_path_loss_reference as hybrid_ref
        import try78_los_path_loss_prior as los_model
    finally:
        sys.path.pop(0)
    return official, hybrid_ref, los_model


def _fresh_term_stats(n_features: int) -> Dict[str, object]:
    return {
        "pixels": 0,
        "coefficient_sum": np.zeros(n_features, dtype=np.float64),
        "feature_sum": np.zeros(n_features, dtype=np.float64),
        "signed_contribution_sum": np.zeros(n_features, dtype=np.float64),
        "absolute_contribution_sum": np.zeros(n_features, dtype=np.float64),
    }


def _add_term_stats(
    stats: MutableMapping[str, Dict[str, object]],
    group: str,
    features: np.ndarray,
    coefficients: np.ndarray,
) -> None:
    n = int(features.shape[0])
    if n == 0:
        return
    rec = stats[group]
    feature_sum = features.sum(axis=0, dtype=np.float64)
    rec["pixels"] = int(rec["pixels"]) + n
    rec["coefficient_sum"] = np.asarray(rec["coefficient_sum"]) + n * coefficients
    rec["feature_sum"] = np.asarray(rec["feature_sum"]) + feature_sum
    rec["signed_contribution_sum"] = (
        np.asarray(rec["signed_contribution_sum"]) + feature_sum * coefficients
    )
    rec["absolute_contribution_sum"] = (
        np.asarray(rec["absolute_contribution_sum"])
        + np.abs(features * coefficients[None, :]).sum(axis=0, dtype=np.float64)
    )


def _fresh_cost_stats() -> Dict[str, float | int]:
    return {
        "pixels": 0,
        "sum_db": 0.0,
        "min_db": float("inf"),
        "max_db": float("-inf"),
        "high_clip_pixels": 0,
    }


def _add_cost_stats(
    stats: MutableMapping[str, Dict[str, float | int]],
    group: str,
    mask: np.ndarray,
    pl_c: np.ndarray,
    path_loss_max_db: float,
) -> None:
    values = pl_c[mask].astype(np.float64, copy=False)
    if values.size == 0:
        return
    rec = stats[group]
    rec["pixels"] = int(rec["pixels"]) + int(values.size)
    rec["sum_db"] = float(rec["sum_db"]) + float(values.sum(dtype=np.float64))
    rec["min_db"] = min(float(rec["min_db"]), float(values.min()))
    rec["max_db"] = max(float(rec["max_db"]), float(values.max()))
    rec["high_clip_pixels"] = int(rec["high_clip_pixels"]) + int(
        (values >= path_loss_max_db).sum()
    )


def _write_csv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    rows = list(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else [])
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hdf5", type=Path, default=DEFAULT_HDF5)
    parser.add_argument("--reference-dir", type=Path, default=DEFAULT_REFERENCE_DIR)
    parser.add_argument("--calibration", type=Path, default=DEFAULT_CALIBRATION)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_ANALYSIS_DIR)
    parser.add_argument("--split-seed", type=int, default=42)
    parser.add_argument("--max-test-maps", type=int, default=None)
    parser.add_argument("--log-every", type=int, default=250)
    args = parser.parse_args()

    official, hybrid_ref, los_model = _import_reference_modules(args.reference_dir)
    refs = los_model.enumerate_samples(args.hdf5)
    _, _, test_refs = official.split_city_holdout_try80(
        refs, val_ratio=0.15, test_ratio=0.15, split_seed=args.split_seed
    )
    if args.max_test_maps is not None:
        test_refs = test_refs[: args.max_test_maps]

    calibration = json.loads(args.calibration.read_text(encoding="utf-8"))
    feature_names = tuple(calibration["feature_names"])
    if feature_names != tuple(final_feature_names(hybrid_ref)):
        raise ValueError("Frozen calibration feature order does not match the COST231 model")
    coefficients = {
        key: np.asarray(value, dtype=np.float64)
        for key, value in calibration["coefficients"].items()
    }
    if any(value.shape != (len(feature_names),) for value in coefficients.values()):
        raise ValueError("Unexpected coefficient-vector length")

    term_stats = defaultdict(lambda: _fresh_term_stats(len(feature_names)))
    cost_stats = defaultdict(_fresh_cost_stats)
    started = time.perf_counter()

    with h5py.File(str(args.hdf5), "r") as handle:
        for number, ref in enumerate(test_refs, start=1):
            sample = hybrid_ref.load_hybrid_sample(handle, ref)
            valid_nlos = sample["valid"] & (sample["los_mask"] == 0)
            topology_class = hybrid_ref.sample_city_type(sample["topology"])
            antenna_bin = hybrid_ref.ant_bin(ref.uav_height_m)
            regime = hybrid_ref.regime_key(topology_class, "NLoS", antenna_bin)
            coef = coefficients[regime]

            pl_c = compute_cost231_map(ref.uav_height_m, hybrid_ref)
            features = hybrid_ref.compute_pixel_features(
                sample["topology"], sample["los_mask"], pl_c, ref.uav_height_m
            )
            nlos_features = features[valid_nlos][:, FEATURE_INDICES].astype(
                np.float64, copy=False
            )
            for group in ("all", topology_class, regime):
                _add_term_stats(term_stats, group, nlos_features, coef)
                _add_cost_stats(
                    cost_stats,
                    group,
                    valid_nlos,
                    pl_c,
                    float(hybrid_ref.PATH_LOSS_MAX_DB),
                )

            if number % max(args.log_every, 1) == 0 or number == len(test_refs):
                elapsed = time.perf_counter() - started
                print(
                    f"audit [{number}/{len(test_refs)}] "
                    f"{number / max(elapsed, 1e-9):.2f} maps/s",
                    flush=True,
                )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    coefficient_rows = []
    for regime in sorted(coefficients):
        topology_class, _, antenna_bin = regime.split("|")
        for feature, value in zip(feature_names, coefficients[regime]):
            coefficient_rows.append(
                {
                    "regime": regime,
                    "topology_class": topology_class,
                    "antenna_bin": antenna_bin,
                    "feature": feature,
                    "coefficient": f"{value:.12g}",
                }
            )
    _write_csv(args.out_dir / "nlos_exact_coefficients.csv", coefficient_rows)

    term_rows = []
    for group in sorted(term_stats):
        rec = term_stats[group]
        n = int(rec["pixels"])
        mean_abs = np.asarray(rec["absolute_contribution_sum"]) / max(n, 1)
        ranks = np.empty(len(feature_names), dtype=np.int64)
        ranks[np.argsort(-mean_abs)] = np.arange(1, len(feature_names) + 1)
        for index, feature in enumerate(feature_names):
            term_rows.append(
                {
                    "group": group,
                    "nlos_pixels": n,
                    "feature": feature,
                    "mean_coefficient": f"{np.asarray(rec['coefficient_sum'])[index] / max(n, 1):.12g}",
                    "mean_feature_value": f"{np.asarray(rec['feature_sum'])[index] / max(n, 1):.12g}",
                    "mean_signed_contribution_db": f"{np.asarray(rec['signed_contribution_sum'])[index] / max(n, 1):.12g}",
                    "mean_absolute_contribution_db": f"{mean_abs[index]:.12g}",
                    "absolute_contribution_rank": int(ranks[index]),
                }
            )
    _write_csv(args.out_dir / "nlos_test_term_audit.csv", term_rows)

    overall_terms = sorted(
        (row for row in term_rows if row["group"] == "all"),
        key=lambda row: int(row["absolute_contribution_rank"]),
    )
    overall_cost = cost_stats["all"]
    n_cost = int(overall_cost["pixels"])
    summary = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "split_contract": {
            "source": "Try 74/75 compatible split_city_holdout_try80",
            "split_seed": args.split_seed,
            "test_maps": len(test_refs),
            "test_cities": sorted(set(ref.city for ref in test_refs)),
        },
        "model": "COST231 NLoS term plus 14-feature regime-specific ridge calibration",
        "features": list(feature_names),
        "regimes": sorted(coefficients),
        "cost231_test_support": {
            "valid_nlos_pixels": n_cost,
            "mean_db": float(overall_cost["sum_db"]) / max(n_cost, 1),
            "min_db": float(overall_cost["min_db"]),
            "max_db": float(overall_cost["max_db"]),
            "high_clip_pixels": int(overall_cost["high_clip_pixels"]),
        },
        "overall_terms_by_mean_absolute_contribution": overall_terms,
        "interpretation": {
            "coefficient_table": "Exact raw-space ridge coefficients; magnitudes are not comparable without feature scale.",
            "term_audit": "Pixel-weighted pre-clipping applied contributions on valid NLoS test targets; descriptive, not causal.",
        },
    }
    (args.out_dir / "nlos_term_audit_summary.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary["cost231_test_support"], indent=2), flush=True)


if __name__ == "__main__":
    main()
