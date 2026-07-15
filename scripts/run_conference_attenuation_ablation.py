"""Reproduce the attenuation-prior ablation on the official Try 80 split.

The split helper is the Try 74/75 compatible city-holdout contract used by
Try 80.  Every calibration is fitted on training cities only.  The script
evaluates the fixed variants on validation and test cities, exports detailed
test statistics, checks the numerical conditioning of the NLoS solve, and
reports visibility shares with building pixels excluded explicitly.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import platform
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple

import h5py
import numpy as np


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
DEFAULT_LOS_CALIBRATION = (
    DEFAULT_TFG_ROOT
    / "TFGpractice"
    / "TFGSeventyEighthTry78"
    / "hybrid_out_try80_split"
    / "calibrations"
    / "try78_los_two_ray_calibration_try80split.json"
)
DEFAULT_OUTPUT = (
    REPO_ROOT
    / "drafts"
    / "conference_attenuation_priors"
    / "data"
    / "official_split_analysis"
)
FINAL_FEATURES = tuple(range(1, 15))
GLOBAL_KEY = "all|NLoS|all_ant"
VARIANT_ORDER = (
    "fspl_raw_nlos",
    "two_ray_raw_nlos",
    "radial_two_ray_raw_nlos",
    "global_nlos_ridge",
    "regime_nlos_ridge",
)
VARIANT_LABELS = {
    "fspl_raw_nlos": "FSPL LoS + raw COST231 NLoS",
    "two_ray_raw_nlos": "coherent two-ray LoS + raw COST231 NLoS",
    "radial_two_ray_raw_nlos": "two-ray + radial LoS + raw COST231 NLoS",
    "global_nlos_ridge": "two-ray + radial LoS + global NLoS ridge",
    "regime_nlos_ridge": "full prior, 9 NLoS regimes",
}
HEIGHT_BINS = (
    (12.0, 50.0, "12--50"),
    (50.0, 150.0, "50--150"),
    (150.0, 300.0, "150--300"),
    (300.0, 500.0001, "300--500"),
)


def _import_reference_modules(reference_dir: Path):
    sys.path.insert(0, str(reference_dir))
    try:
        import run_try78_on_try80_split as official
        import try78_hybrid_path_loss_reference as hybrid_ref
        import try78_los_path_loss_prior as los_model
    finally:
        sys.path.pop(0)
    return official, hybrid_ref, los_model


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: Sequence[Mapping[str, object]], fields: Sequence[str] | None = None) -> None:
    rows = list(rows)
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def compute_cost231_map(h_tx: float, hybrid_ref) -> np.ndarray:
    """Return the clipped COST231-shaped NLoS map used by every fitted model."""
    h_tx_c = max(float(h_tx), 1.0)
    h_rx_c = max(float(hybrid_ref.RX_HEIGHT_M), 0.5)
    d2d = np.maximum(np.asarray(hybrid_ref._D2D, dtype=np.float64), 1.0)
    freq_mhz = float(hybrid_ref.FREQ_GHZ) * 1000.0
    log_f = math.log10(freq_mhz)
    a_hm = (1.1 * log_f - 0.7) * h_rx_c - (1.56 * log_f - 0.8)
    d_km = np.maximum(d2d / 1000.0, 0.001)
    hb_log = math.log10(h_tx_c)
    path_loss = (
        46.3
        + 33.9 * log_f
        - 13.82 * hb_log
        - a_hm
        + (44.9 - 6.55 * hb_log) * np.log10(d_km)
        + 3.0
    )
    return np.clip(path_loss, 0.0, float(hybrid_ref.PATH_LOSS_MAX_DB)).astype(np.float32)


def final_feature_names(hybrid_ref) -> List[str]:
    names = [hybrid_ref.FEATURE_NAMES[index] for index in FINAL_FEATURES]
    names[0] = "pl_c"
    return names


def _fresh_error_stats() -> Dict[str, float | int]:
    return {"sse": 0.0, "sae": 0.0, "n": 0}


def _add_error(stats: MutableMapping[str, float | int], pred: np.ndarray, target: np.ndarray, mask: np.ndarray) -> None:
    if not np.any(mask):
        return
    error = pred[mask].astype(np.float64) - target[mask].astype(np.float64)
    stats["sse"] = float(stats["sse"]) + float(error @ error)
    stats["sae"] = float(stats["sae"]) + float(np.abs(error).sum())
    stats["n"] = int(stats["n"]) + int(error.size)


def _summarize_error(stats: Mapping[str, float | int], prefix: str = "") -> Dict[str, float | int]:
    n = int(stats["n"])
    root = math.sqrt(float(stats["sse"]) / n) if n else float("nan")
    mae = float(stats["sae"]) / n if n else float("nan")
    return {f"{prefix}rmse_db": root, f"{prefix}mae_db": mae, f"{prefix}pixels": n}


def _corr(pred: np.ndarray, target: np.ndarray, mask: np.ndarray) -> float:
    x = pred[mask].astype(np.float64)
    y = target[mask].astype(np.float64)
    if x.size < 2:
        return float("nan")
    x -= x.mean()
    y -= y.mean()
    den = float(np.linalg.norm(x) * np.linalg.norm(y))
    return float(x @ y / den) if den > 0.0 else float("nan")


def _new_raw_equations(p: int) -> Dict[str, object]:
    return {
        "n": 0,
        "xtx": np.zeros((p, p), dtype=np.float64),
        "xty": np.zeros(p, dtype=np.float64),
        "sum_y2": 0.0,
    }


def _fit_from_raw_equations(
    item: Mapping[str, object], ridge_lambda: float
) -> Tuple[np.ndarray, Dict[str, float | int | List[float]]]:
    """Solve standardized ridge from one-pass raw normal equations."""
    n = int(item["n"])
    xtx = np.asarray(item["xtx"], dtype=np.float64)
    xty = np.asarray(item["xty"], dtype=np.float64)
    p = xtx.shape[0]
    mean = xtx[-1, :-1] / max(n, 1)
    variance = np.diag(xtx)[:-1] / max(n, 1) - np.square(mean)
    std = np.sqrt(np.maximum(variance, 1e-8))
    std[std < 1e-4] = 1.0

    transform = np.zeros((p, p), dtype=np.float64)
    transform[np.arange(p - 1), np.arange(p - 1)] = 1.0 / std
    transform[-1, :-1] = -mean / std
    transform[-1, -1] = 1.0
    ztz = transform.T @ xtx @ transform
    zty = transform.T @ xty
    regularizer = ridge_lambda * np.eye(p, dtype=np.float64)
    regularizer[-1, -1] = 0.0
    beta_std = np.linalg.solve(ztz + regularizer, zty)
    beta_raw = transform @ beta_std

    raw_cond = float(np.sqrt(np.linalg.cond(xtx)))
    standardized_cond = float(np.sqrt(np.linalg.cond(ztz)))
    sse = (
        float(item["sum_y2"])
        - 2.0 * float(beta_raw @ xty)
        + float(beta_raw @ xtx @ beta_raw)
    )
    diagnostics: Dict[str, float | int | List[float]] = {
        "fit_pixels": n,
        "fit_rmse_db": math.sqrt(max(sse, 0.0) / max(n, 1)),
        "raw_design_condition": raw_cond,
        "standardized_design_condition": standardized_cond,
        "feature_mean": mean.tolist(),
        "feature_std": std.tolist(),
    }
    return beta_raw, diagnostics


def fit_nlos_models(
    hdf5_path: Path,
    fit_refs: Sequence[object],
    official,
    hybrid_ref,
    *,
    max_pixels: int,
    ridge_lambda: float,
    seed: int,
    log_every: int,
) -> Tuple[Dict[str, Dict[str, np.ndarray]], Dict[str, object]]:
    specs = {
        "regime_nlos_ridge": (FINAL_FEATURES, True),
        "global_nlos_ridge": (FINAL_FEATURES, False),
    }
    equations: Dict[str, Dict[str, Dict[str, object]]] = {name: {} for name in specs}
    started = time.perf_counter()
    with h5py.File(str(hdf5_path), "r") as handle:
        for number, ref in enumerate(fit_refs, start=1):
            sample = hybrid_ref.load_hybrid_sample(handle, ref)
            valid_nlos = sample["valid"] & (sample["los_mask"] == 0)
            if np.any(valid_nlos):
                city_type = hybrid_ref.sample_city_type(sample["topology"])
                antenna_bin = hybrid_ref.ant_bin(ref.uav_height_m)
                regime = hybrid_ref.regime_key(city_type, "NLoS", antenna_bin)
                prior = compute_cost231_map(ref.uav_height_m, hybrid_ref)
                features = hybrid_ref.compute_pixel_features(
                    sample["topology"], sample["los_mask"], prior, ref.uav_height_m
                ).reshape(-1, hybrid_ref.N_FEAT)
                y = sample["path_loss"].reshape(-1).astype(np.float64, copy=False)
                picked = official._select_flat_indices(
                    valid_nlos,
                    max_pixels=max_pixels,
                    seed=official._stable_sample_seed(seed, ref.city, ref.sample, "NLoS"),
                )
                for model_name, (feature_indices, regime_specific) in specs.items():
                    key = regime if regime_specific else GLOBAL_KEY
                    x = features[picked][:, feature_indices].astype(np.float64, copy=False)
                    target = y[picked]
                    item = equations[model_name].setdefault(key, _new_raw_equations(x.shape[1]))
                    item["n"] = int(item["n"]) + int(x.shape[0])
                    item["xtx"] = np.asarray(item["xtx"]) + x.T @ x
                    item["xty"] = np.asarray(item["xty"]) + x.T @ target
                    item["sum_y2"] = float(item["sum_y2"]) + float(target @ target)

            if number % max(log_every, 1) == 0 or number == len(fit_refs):
                elapsed = time.perf_counter() - started
                print(
                    f"fit NLoS [{number}/{len(fit_refs)}] "
                    f"{number / max(elapsed, 1e-9):.2f} maps/s",
                    flush=True,
                )

    coefs: Dict[str, Dict[str, np.ndarray]] = {}
    diagnostics: Dict[str, object] = {}
    for model_name, model_equations in equations.items():
        coefs[model_name] = {}
        model_diag: Dict[str, object] = {}
        for key in sorted(model_equations):
            beta, diag = _fit_from_raw_equations(model_equations[key], ridge_lambda)
            coefs[model_name][key] = beta
            model_diag[key] = diag
        diagnostics[model_name] = model_diag
    diagnostics["fit_contract"] = {
        "training_maps": len(fit_refs),
        "max_nlos_pixels_per_map": max_pixels,
        "ridge_lambda": ridge_lambda,
        "seed": seed,
        "standardization": "nonbias features standardized within each fitted model",
    }
    return coefs, diagnostics


def _save_calibration(
    path: Path,
    model_name: str,
    feature_names: Sequence[str],
    coefs: Mapping[str, np.ndarray],
    diagnostics: Mapping[str, object],
) -> None:
    _write_json(
        path,
        {
            "model_type": model_name,
            "feature_names": list(feature_names),
            "coefficients": {key: value.tolist() for key, value in coefs.items()},
            "diagnostics": diagnostics,
        },
    )


def _two_ray_without_radial(h_tx: float, calibration: Mapping[str, np.ndarray], los_model) -> np.ndarray:
    rho = los_model._interpolate_scalar(h_tx, calibration["height_bins_m"], calibration["rho"])
    phi = los_model._interpolate_scalar(h_tx, calibration["height_bins_m"], calibration["phi_rad"])
    bias = los_model._interpolate_scalar(h_tx, calibration["height_bins_m"], calibration["bias_db"])
    pred = (
        los_model.fspl_db(h_tx)
        + los_model.coherent_two_ray_correction_db(h_tx, rho=rho, phi_rad=phi)
        + bias
    )
    return np.clip(pred, los_model.PATH_LOSS_MIN_DB, los_model.PATH_LOSS_MAX_DB).astype(np.float32)


def _linear_nlos_map(
    features: np.ndarray,
    feature_indices: Sequence[int],
    coef: np.ndarray,
    hybrid_ref,
) -> np.ndarray:
    selected = features[..., feature_indices]
    pred = np.einsum("ijk,k->ij", selected, coef, optimize=True)
    return np.clip(pred, hybrid_ref.PATH_LOSS_MIN_DB, hybrid_ref.PATH_LOSS_MAX_DB).astype(np.float32)


def predict_variants(
    sample: Mapping[str, np.ndarray],
    ref,
    two_ray_calibration: Mapping[str, np.ndarray],
    coefs: Mapping[str, Mapping[str, np.ndarray]],
    hybrid_ref,
    los_model,
) -> Tuple[Dict[str, np.ndarray], Dict[str, object]]:
    h_tx = ref.uav_height_m
    los_flag = sample["los_mask"] > 0
    city_type = hybrid_ref.sample_city_type(sample["topology"])
    antenna_bin = hybrid_ref.ant_bin(h_tx)
    regime = hybrid_ref.regime_key(city_type, "NLoS", antenna_bin)
    prior = compute_cost231_map(h_tx, hybrid_ref)
    features = hybrid_ref.compute_pixel_features(sample["topology"], sample["los_mask"], prior, h_tx)
    fspl = los_model.fspl_db(h_tx)
    two_ray = _two_ray_without_radial(h_tx, two_ray_calibration, los_model)
    full_los = los_model.predict_two_ray_map(h_tx, two_ray_calibration)
    global_nlos = _linear_nlos_map(
        features, FINAL_FEATURES, coefs["global_nlos_ridge"][GLOBAL_KEY], hybrid_ref
    )
    regime_nlos = _linear_nlos_map(
        features, FINAL_FEATURES, coefs["regime_nlos_ridge"][regime], hybrid_ref
    )

    predictions = {
        "fspl_raw_nlos": np.where(los_flag, fspl, prior).astype(np.float32),
        "two_ray_raw_nlos": np.where(los_flag, two_ray, prior).astype(np.float32),
        "radial_two_ray_raw_nlos": np.where(los_flag, full_los, prior).astype(np.float32),
        "global_nlos_ridge": np.where(los_flag, full_los, global_nlos).astype(np.float32),
        "regime_nlos_ridge": np.where(los_flag, full_los, regime_nlos).astype(np.float32),
    }
    return predictions, {
        "city_type": city_type,
        "antenna_bin": antenna_bin,
        "regime": regime,
        "pl_c": prior,
        "features": features,
    }


def _metric_bundle() -> Dict[str, Dict[str, float | int]]:
    return {name: _fresh_error_stats() for name in ("overall", "los", "nlos")}


def _summary_bundle(bundle: Mapping[str, Mapping[str, float | int]]) -> Dict[str, float | int]:
    out: Dict[str, float | int] = {}
    for region in ("overall", "los", "nlos"):
        out.update(_summarize_error(bundle[region], prefix=f"{region}_"))
    return out


def evaluate_split(
    split_name: str,
    hdf5_path: Path,
    refs: Sequence[object],
    two_ray_calibration: Mapping[str, np.ndarray],
    coefs: Mapping[str, Mapping[str, np.ndarray]],
    hybrid_ref,
    los_model,
    *,
    log_every: int,
    collect_details: bool,
) -> Dict[str, object]:
    aggregate = {variant: _metric_bundle() for variant in VARIANT_ORDER}
    correlation_sum = defaultdict(float)
    correlation_weight = defaultdict(int)
    per_map: List[Dict[str, object]] = []
    city_stats: Dict[str, Dict[str, Dict[str, float | int]]] = defaultdict(_metric_bundle)
    city_corr_sum = defaultdict(float)
    city_corr_weight = defaultdict(int)
    height_stats: Dict[str, Dict[str, Dict[str, float | int]]] = defaultdict(_metric_bundle)
    height_maps = defaultdict(int)
    visibility = {
        "full_cells": 0,
        "ground_cells": 0,
        "building_cells": 0,
        "valid_ground_cells": 0,
        "invalid_ground_cells": 0,
        "los_ground_cells": 0,
        "nlos_ground_cells": 0,
        "valid_los_cells": 0,
        "valid_nlos_cells": 0,
    }
    nlos_fractions_valid: List[float] = []
    nlos_fractions_ground: List[float] = []
    cancellation = {
        "regime_nlos_ridge": defaultdict(
            lambda: {"pixels": 0, "abs_terms": 0.0, "abs_prediction": 0.0}
        )
    }

    started = time.perf_counter()
    with h5py.File(str(hdf5_path), "r") as handle:
        for number, ref in enumerate(refs, start=1):
            sample = hybrid_ref.load_hybrid_sample(handle, ref)
            valid = sample["valid"]
            ground = sample["ground"]
            los_ground = ground & (sample["los_mask"] > 0)
            nlos_ground = ground & (sample["los_mask"] == 0)
            los = valid & (sample["los_mask"] > 0)
            nlos = valid & (sample["los_mask"] == 0)
            predictions, aux = predict_variants(
                sample, ref, two_ray_calibration, coefs, hybrid_ref, los_model
            )
            target = sample["path_loss"]
            height_label = next(
                (label for low, high, label in HEIGHT_BINS if low <= ref.uav_height_m < high),
                "outside_reported_bins",
            )

            if collect_details:
                visibility["full_cells"] += int(valid.size)
                visibility["ground_cells"] += int(ground.sum())
                visibility["building_cells"] += int((~ground).sum())
                visibility["valid_ground_cells"] += int(valid.sum())
                visibility["invalid_ground_cells"] += int((ground & ~valid).sum())
                visibility["los_ground_cells"] += int(los_ground.sum())
                visibility["nlos_ground_cells"] += int(nlos_ground.sum())
                visibility["valid_los_cells"] += int(los.sum())
                visibility["valid_nlos_cells"] += int(nlos.sum())
                nlos_fractions_valid.append(float(nlos.sum() / max(valid.sum(), 1)))
                nlos_fractions_ground.append(float(nlos_ground.sum() / max(ground.sum(), 1)))
                height_maps[height_label] += 1

            for variant, pred in predictions.items():
                _add_error(aggregate[variant]["overall"], pred, target, valid)
                _add_error(aggregate[variant]["los"], pred, target, los)
                _add_error(aggregate[variant]["nlos"], pred, target, nlos)
                corr = _corr(pred, target, valid)
                if np.isfinite(corr):
                    correlation_sum[variant] += corr * int(valid.sum())
                    correlation_weight[variant] += int(valid.sum())

            if collect_details:
                final_pred = predictions["regime_nlos_ridge"]
                for region, mask in (("overall", valid), ("los", los), ("nlos", nlos)):
                    _add_error(city_stats[ref.city][region], final_pred, target, mask)
                    _add_error(height_stats[height_label][region], final_pred, target, mask)
                corr = _corr(final_pred, target, valid)
                if np.isfinite(corr):
                    city_corr_sum[ref.city] += corr * int(valid.sum())
                    city_corr_weight[ref.city] += int(valid.sum())
                map_row: Dict[str, object] = {
                    "city": ref.city,
                    "sample": ref.sample,
                    "uav_height_m": ref.uav_height_m,
                    "topology_class": aux["city_type"],
                    "antenna_bin": aux["antenna_bin"],
                    "height_bin": height_label,
                    "valid_pixels": int(valid.sum()),
                    "los_pixels": int(los.sum()),
                    "nlos_pixels": int(nlos.sum()),
                    "nlos_share_valid": float(nlos.sum() / max(valid.sum(), 1)),
                    "correlation": corr,
                }
                for region, mask in (("overall", valid), ("los", los), ("nlos", nlos)):
                    local = _fresh_error_stats()
                    _add_error(local, final_pred, target, mask)
                    map_row.update(_summarize_error(local, prefix=f"{region}_"))
                per_map.append(map_row)

                features = np.asarray(aux["features"])
                regime = str(aux["regime"])
                for model_name, indices in (("regime_nlos_ridge", FINAL_FEATURES),):
                    x = features[nlos][:, indices].astype(np.float64, copy=False)
                    coef = coefs[model_name][regime]
                    terms = x * coef[None, :]
                    raw_prediction = terms.sum(axis=1)
                    for key in (regime, "all"):
                        rec = cancellation[model_name][key]
                        rec["pixels"] += int(x.shape[0])
                        rec["abs_terms"] += float(np.abs(terms).sum())
                        rec["abs_prediction"] += float(np.abs(raw_prediction).sum())

            if number % max(log_every, 1) == 0 or number == len(refs):
                elapsed = time.perf_counter() - started
                final_stats = aggregate["regime_nlos_ridge"]["overall"]
                current = math.sqrt(float(final_stats["sse"]) / max(int(final_stats["n"]), 1))
                print(
                    f"evaluate {split_name} [{number}/{len(refs)}] "
                    f"RMSE={current:.4f} dB, {number / max(elapsed, 1e-9):.2f} maps/s",
                    flush=True,
                )

    rows: List[Dict[str, object]] = []
    for variant in VARIANT_ORDER:
        row: Dict[str, object] = {
            "split": split_name,
            "variant": variant,
            "label": VARIANT_LABELS[variant],
            **_summary_bundle(aggregate[variant]),
            "map_correlation": (
                correlation_sum[variant] / correlation_weight[variant]
                if correlation_weight[variant]
                else float("nan")
            ),
            "maps": len(refs),
        }
        rows.append(row)

    result: Dict[str, object] = {"ablation_rows": rows}
    if collect_details:
        city_rows = []
        for city in sorted(city_stats):
            city_rows.append(
                {
                    "city": city,
                    **_summary_bundle(city_stats[city]),
                    "map_correlation": city_corr_sum[city] / max(city_corr_weight[city], 1),
                    "maps": sum(1 for row in per_map if row["city"] == city),
                }
            )
        height_rows = []
        for _, _, label in HEIGHT_BINS:
            height_rows.append(
                {"height_bin": label, **_summary_bundle(height_stats[label]), "maps": height_maps[label]}
            )
        cancellation_rows = []
        for model_name in cancellation:
            for group in sorted(cancellation[model_name]):
                rec = cancellation[model_name][group]
                cancellation_rows.append(
                    {
                        "model": model_name,
                        "group": group,
                        "nlos_pixels": rec["pixels"],
                        "mean_sum_abs_terms_db": rec["abs_terms"] / max(rec["pixels"], 1),
                        "mean_abs_raw_prediction_db": rec["abs_prediction"] / max(rec["pixels"], 1),
                        "cancellation_ratio": rec["abs_terms"] / max(rec["abs_prediction"], 1e-12),
                    }
                )
        quantiles_valid = np.quantile(
            np.asarray(nlos_fractions_valid), [0, 0.25, 0.5, 0.75, 0.95, 1]
        ).tolist()
        quantiles_ground = np.quantile(
            np.asarray(nlos_fractions_ground), [0, 0.25, 0.5, 0.75, 0.95, 1]
        ).tolist()
        visibility_summary = {
            **visibility,
            "los_share_ground": visibility["los_ground_cells"] / max(visibility["ground_cells"], 1),
            "nlos_share_ground": visibility["nlos_ground_cells"] / max(visibility["ground_cells"], 1),
            "los_share_valid_ground": visibility["valid_los_cells"] / max(visibility["valid_ground_cells"], 1),
            "nlos_share_valid_ground": visibility["valid_nlos_cells"] / max(visibility["valid_ground_cells"], 1),
            "building_share_full_map": visibility["building_cells"] / max(visibility["full_cells"], 1),
            "invalid_ground_share_ground": visibility["invalid_ground_cells"] / max(visibility["ground_cells"], 1),
            "per_map_nlos_share_valid_quantiles": dict(
                zip(("min", "q25", "median", "q75", "q95", "max"), quantiles_valid)
            ),
            "per_map_nlos_share_ground_quantiles": dict(
                zip(("min", "q25", "median", "q75", "q95", "max"), quantiles_ground)
            ),
        }
        result.update(
            {
                "per_map": per_map,
                "per_city": city_rows,
                "per_height": height_rows,
                "visibility": visibility_summary,
                "cancellation": cancellation_rows,
            }
        )
    return result


def bootstrap_cities(city_rows: Sequence[Mapping[str, object]], *, draws: int, seed: int) -> Dict[str, object]:
    rng = np.random.default_rng(seed)
    regions = ("overall", "los", "nlos")
    n_cities = len(city_rows)
    arrays = {}
    for region in regions:
        n = np.asarray([row[f"{region}_pixels"] for row in city_rows], dtype=np.float64)
        rmse = np.asarray([row[f"{region}_rmse_db"] for row in city_rows], dtype=np.float64)
        mae = np.asarray([row[f"{region}_mae_db"] for row in city_rows], dtype=np.float64)
        arrays[region] = {"n": n, "sse": n * np.square(rmse), "sae": n * mae}

    bootstrap_values = {f"{region}_{metric}": np.empty(draws, dtype=np.float64)
                        for region in regions for metric in ("rmse_db", "mae_db")}
    macro = np.empty(draws, dtype=np.float64)
    map_correlation = np.empty(draws, dtype=np.float64)
    corr_weight = np.asarray([row["overall_pixels"] for row in city_rows], dtype=np.float64)
    corr_value = np.asarray([row["map_correlation"] for row in city_rows], dtype=np.float64)
    for start in range(0, draws, 1000):
        stop = min(start + 1000, draws)
        picked = rng.integers(0, n_cities, size=(stop - start, n_cities))
        for region in regions:
            data = arrays[region]
            n_sum = data["n"][picked].sum(axis=1)
            sse_sum = data["sse"][picked].sum(axis=1)
            sae_sum = data["sae"][picked].sum(axis=1)
            bootstrap_values[f"{region}_rmse_db"][start:stop] = np.sqrt(sse_sum / n_sum)
            bootstrap_values[f"{region}_mae_db"][start:stop] = sae_sum / n_sum
        macro[start:stop] = np.asarray(
            [city_rows[i]["overall_rmse_db"] for i in range(n_cities)], dtype=np.float64
        )[picked].mean(axis=1)
        selected_weight = corr_weight[picked]
        map_correlation[start:stop] = (
            (selected_weight * corr_value[picked]).sum(axis=1) / selected_weight.sum(axis=1)
        )

    intervals = {}
    for name, values in {
        **bootstrap_values,
        "macro_city_rmse_db": macro,
        "map_correlation": map_correlation,
    }.items():
        lo, median, hi = np.quantile(values, [0.025, 0.5, 0.975])
        intervals[name] = {"low_95": float(lo), "median": float(median), "high_95": float(hi)}
    return {
        "unit": "held-out city",
        "cities": n_cities,
        "draws": draws,
        "seed": seed,
        "method": "percentile bootstrap, cities sampled with replacement; pixel-weighted metrics recomputed",
        "intervals": intervals,
    }


def conditioning_rows(
    diagnostics: Mapping[str, object],
    coefs: Mapping[str, Mapping[str, np.ndarray]],
    hybrid_ref,
) -> List[Dict[str, object]]:
    rows = []
    for model_name in ("regime_nlos_ridge", "global_nlos_ridge"):
        feature_names = final_feature_names(hybrid_ref)
        for key, diag in sorted(diagnostics[model_name].items()):
            rows.append(
                {
                    "model": model_name,
                    "regime": key,
                    "features": len(feature_names),
                    "feature_names": ";".join(feature_names),
                    "fit_pixels": diag["fit_pixels"],
                    "fit_rmse_db": diag["fit_rmse_db"],
                    "raw_design_condition": diag["raw_design_condition"],
                    "standardized_design_condition": diag["standardized_design_condition"],
                    "max_abs_raw_coefficient": float(np.max(np.abs(coefs[model_name][key]))),
                }
            )
    return rows


def benchmark_prior(
    hdf5_path: Path,
    refs: Sequence[object],
    two_ray_calibration: Mapping[str, np.ndarray],
    coefs: Mapping[str, Mapping[str, np.ndarray]],
    hybrid_ref,
    los_model,
    *,
    maps: int,
) -> Dict[str, object]:
    picked = list(refs[: min(maps, len(refs))])
    read_times = []
    core_times = []
    with h5py.File(str(hdf5_path), "r") as handle:
        for ref in picked:
            started = time.perf_counter()
            sample = hybrid_ref.load_hybrid_sample(handle, ref)
            read_times.append(time.perf_counter() - started)
            started = time.perf_counter()
            city_type = hybrid_ref.sample_city_type(sample["topology"])
            antenna_bin = hybrid_ref.ant_bin(ref.uav_height_m)
            regime = hybrid_ref.regime_key(city_type, "NLoS", antenna_bin)
            prior = compute_cost231_map(ref.uav_height_m, hybrid_ref)
            features = hybrid_ref.compute_pixel_features(
                sample["topology"], sample["los_mask"], prior, ref.uav_height_m
            )
            nlos = _linear_nlos_map(
                features,
                FINAL_FEATURES,
                coefs["regime_nlos_ridge"][regime],
                hybrid_ref,
            )
            los = los_model.predict_two_ray_map(ref.uav_height_m, two_ray_calibration)
            prediction = np.where(sample["los_mask"] > 0, los, nlos)
            _ = float(prediction.mean())
            core_times.append(time.perf_counter() - started)
    prior_median = float(np.median(core_times))
    prior_p95 = float(np.quantile(core_times, 0.95))
    matlab_rt_median = 102.2887378
    return {
        "maps": len(picked),
        "hardware": {
            "platform": platform.platform(),
            "processor": platform.processor() or os.environ.get("PROCESSOR_IDENTIFIER", "unknown"),
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "scope": "HDF5 read measured separately; core computes one final prior map from the cached configured-ray-tracer visibility mask and the COST231 NLoS term",
        "hdf5_read_median_s": float(np.median(read_times)),
        "hdf5_read_p95_s": float(np.quantile(read_times, 0.95)),
        "prior_core_median_s": prior_median,
        "prior_core_p95_s": prior_p95,
        "external_ray_tracing_reference": {
            "maps": 5,
            "seed": 20260715,
            "median_s_per_map": matlab_rt_median,
            "mean_s_per_map": 142.85610778,
            "p95_s_per_map": 241.59120804,
            "min_s_per_map": 91.4517301,
            "max_s_per_map": 260.3095472,
            "hardware": "AMD Ryzen 5 5600X CPU; GPU disabled for both measured paths",
            "software": "MATLAB R2024b Update 1",
            "configuration": {
                "city": "Barcelona",
                "transmitter_heights_per_layout": 1,
                "receiver_grid_resolution_m": 1,
                "max_reflections": 1,
                "max_diffractions": 0,
            },
            "scope": "attenuation, delay spread, and angular spread",
            "visibility_repeat_audit": {
                "conditions": 5,
                "receiver_comparisons": 742392,
                "bit_differences": 0,
                "all_equal": True,
                "identity_key": "city geometry, transmitter position and height, receiver grid, and ray-tracing settings",
            },
            "raw_median_wall_clock_ratio_vs_prior": matlab_rt_median / prior_median,
            "comparability": "same CPU and spatial resolution, but different output scope and timing boundaries; the ratio is not a like-for-like algorithmic speedup",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hdf5", type=Path, default=DEFAULT_HDF5)
    parser.add_argument("--reference-dir", type=Path, default=DEFAULT_REFERENCE_DIR)
    parser.add_argument("--los-calibration", type=Path, default=DEFAULT_LOS_CALIBRATION)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--split-seed", type=int, default=42)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--ridge-lambda", type=float, default=1e-2)
    parser.add_argument("--nlos-pixels-per-map", type=int, default=1024)
    parser.add_argument("--bootstrap-draws", type=int, default=20000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260715)
    parser.add_argument("--runtime-maps", type=int, default=100)
    parser.add_argument("--max-fit-maps", type=int, default=None)
    parser.add_argument("--max-val-maps", type=int, default=None)
    parser.add_argument("--max-test-maps", type=int, default=None)
    parser.add_argument("--log-every", type=int, default=250)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    official, hybrid_ref, los_model = _import_reference_modules(args.reference_dir)
    refs = los_model.enumerate_samples(args.hdf5)
    train_refs, val_refs, test_refs = official.split_city_holdout_try80(
        refs, val_ratio=0.15, test_ratio=0.15, split_seed=args.split_seed
    )
    if args.max_fit_maps is not None:
        train_refs = los_model.subsample_refs(train_refs, args.max_fit_maps, args.seed)
    if args.max_val_maps is not None:
        val_refs = los_model.subsample_refs(val_refs, args.max_val_maps, args.seed + 1)
    if args.max_test_maps is not None:
        test_refs = los_model.subsample_refs(test_refs, args.max_test_maps, args.seed + 2)
    print(
        f"official split: train={len(train_refs)} ({len(set(r.city for r in train_refs))} cities), "
        f"val={len(val_refs)} ({len(set(r.city for r in val_refs))}), "
        f"test={len(test_refs)} ({len(set(r.city for r in test_refs))})",
        flush=True,
    )

    _, two_ray_calibration = los_model.load_calibration(args.los_calibration)
    coefs, fit_diagnostics = fit_nlos_models(
        args.hdf5,
        train_refs,
        official,
        hybrid_ref,
        max_pixels=args.nlos_pixels_per_map,
        ridge_lambda=args.ridge_lambda,
        seed=args.seed,
        log_every=args.log_every,
    )
    feature_names = final_feature_names(hybrid_ref)
    _save_calibration(
        args.out_dir / "nlos_regime_calibration_official.json",
        "regime_nlos_ridge_cost231",
        feature_names,
        coefs["regime_nlos_ridge"],
        fit_diagnostics["regime_nlos_ridge"],
    )
    _save_calibration(
        args.out_dir / "nlos_global_calibration_official.json",
        "global_nlos_ridge_cost231",
        feature_names,
        coefs["global_nlos_ridge"],
        fit_diagnostics["global_nlos_ridge"],
    )

    val_result = evaluate_split(
        "validation",
        args.hdf5,
        val_refs,
        two_ray_calibration,
        coefs,
        hybrid_ref,
        los_model,
        log_every=args.log_every,
        collect_details=False,
    )
    _write_csv(args.out_dir / "validation_ablation_metrics.csv", val_result["ablation_rows"])
    test_result = evaluate_split(
        "test",
        args.hdf5,
        test_refs,
        two_ray_calibration,
        coefs,
        hybrid_ref,
        los_model,
        log_every=args.log_every,
        collect_details=True,
    )
    ablation_rows = list(val_result["ablation_rows"]) + list(test_result["ablation_rows"])
    _write_csv(args.out_dir / "ablation_metrics.csv", ablation_rows)
    _write_csv(args.out_dir / "official_test_per_map_metrics.csv", test_result["per_map"])
    _write_csv(args.out_dir / "official_test_per_city_metrics.csv", test_result["per_city"])
    _write_csv(args.out_dir / "official_test_height_metrics.csv", test_result["per_height"])
    _write_csv(args.out_dir / "nlos_cancellation_diagnostics.csv", test_result["cancellation"])
    condition = conditioning_rows(fit_diagnostics, coefs, hybrid_ref)
    _write_csv(args.out_dir / "nlos_conditioning.csv", condition)

    bootstrap = bootstrap_cities(
        test_result["per_city"], draws=args.bootstrap_draws, seed=args.bootstrap_seed
    )
    runtime = benchmark_prior(
        args.hdf5,
        test_refs,
        two_ray_calibration,
        coefs,
        hybrid_ref,
        los_model,
        maps=args.runtime_maps,
    )
    test_final = next(
        row for row in test_result["ablation_rows"] if row["variant"] == "regime_nlos_ridge"
    )
    summary = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "split_contract": {
            "source": "Try 74/75 compatible split_city_holdout_try80",
            "split_seed": args.split_seed,
            "train_maps": len(train_refs),
            "validation_maps": len(val_refs),
            "test_maps": len(test_refs),
            "train_cities": sorted(set(r.city for r in train_refs)),
            "validation_cities": sorted(set(r.city for r in val_refs)),
            "test_cities": sorted(set(r.city for r in test_refs)),
            "calibration_membership": "training cities only",
        },
        "final_variant": {
            "name": "regime_nlos_ridge",
            "selection_reason": "observable topology and transmitter-height regimes selected on the validation component ablation; no test-set tuning",
            "test_metrics": test_final,
        },
        "visibility_shares": test_result["visibility"],
        "city_bootstrap": bootstrap,
        "macro_city_rmse_db": float(
            np.mean([row["overall_rmse_db"] for row in test_result["per_city"]])
        ),
        "visibility_contract": {
            "source": "binary LineOfSight output from the configured MATLAB ray tracer, stored with each HDF5 sample",
            "identity_key": "city geometry, transmitter position and height, receiver grid, and ray-tracing settings",
            "receiver_support": "topology_map == 0; building pixels are excluded before LoS/NLoS shares and metrics",
        },
        "runtime": runtime,
        "fit_contract": fit_diagnostics["fit_contract"],
    }
    _write_json(args.out_dir / "official_test_summary.json", summary)
    print(json.dumps(summary, indent=2, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
