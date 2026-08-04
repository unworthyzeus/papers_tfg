"""Generate the conference paper's held-out LoS/NLoS qualitative example.

The figure calls the frozen prior implementation directly.  It is therefore a
data visualization of the deployed artifact, not an illustrative redraw.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import h5py
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from run_conference_attenuation_ablation import compute_cost231_map


REPO_ROOT = Path(__file__).resolve().parents[1]
HDF5_PATH = Path(r"C:\TFG\TFGpractice\Datasets\CKM_Dataset_270326.h5")
REFERENCE_DIR = Path(r"C:\TFG\TFGpractice\TFGEightiethTry80\scripts\recalibrate_priors")
EXPERIMENT_DIR = REPO_ROOT / "experiments" / "itu_topology_building_max_ablation"
CALIBRATION = EXPERIMENT_DIR / "results" / "two_ray_itu3_building_max" / "nlos_regime_calibration_itu.json"
LOS_CALIBRATION = EXPERIMENT_DIR / "results" / "two_ray_itu3_building_max" / "los_two_ray_refitted_calibration.json"
OUTPUT = REPO_ROOT / "drafts" / "conference_attenuation_priors" / "figures" / "nlos_heldout_example.png"
CITY = "Vancouver"
SAMPLE = "sample_15262"


def masked(values: np.ndarray, keep: np.ndarray) -> np.ma.MaskedArray:
    return np.ma.array(values, mask=~keep)


def main() -> None:
    sys.path.insert(0, str(REFERENCE_DIR))
    import try78_hybrid_path_loss_reference as priors
    import try78_los_path_loss_prior as los_model
    sys.path.insert(0, str(EXPERIMENT_DIR))
    from itu_topology import ITUTopologyRouter

    router = ITUTopologyRouter(
        mode="itu3",
        meters_per_pixel=float(priors.METERS_PER_PIXEL),
        connectivity=4,
        min_component_area_m2=1.0,
    )
    priors.sample_city_type = router.classify

    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    coefficients = {
        key: np.asarray(value, dtype=np.float64)
        for key, value in calibration["coefficients"].items()
    }
    _, los_calibration = los_model.load_calibration(LOS_CALIBRATION)

    with h5py.File(HDF5_PATH, "r") as handle:
        group = handle[CITY][SAMPLE]
        topology = np.asarray(group["topology_map"][...], dtype=np.float32)
        los_mask = np.asarray(group["los_mask"][...], dtype=np.float32)
        target = np.asarray(group["path_loss"][...], dtype=np.float32)
        h_tx = float(np.asarray(group["uav_height"][...]).reshape(-1)[0])

    raw = compute_cost231_map(h_tx, priors)
    features = priors.compute_pixel_features(topology, los_mask, raw, h_tx)
    topology_class = priors.sample_city_type(topology)
    antenna_bin = priors.ant_bin(h_tx)
    key = f"{topology_class}|NLoS|{antenna_bin}"
    coef = coefficients[key]
    nlos_prior = np.clip(
        features[..., 1:] @ coef, priors.PATH_LOSS_MIN_DB, priors.PATH_LOSS_MAX_DB
    )
    los_prior = los_model.predict_two_ray_map(h_tx, los_calibration)

    ground = topology == 0.0
    valid = ground & np.isfinite(target) & (target >= priors.PATH_LOSS_MIN_DB)
    los = valid & (los_mask > 0.5)
    nlos = valid & (los_mask <= 0.5)
    prediction = np.where(los_mask > 0.5, los_prior, nlos_prior)
    los_error = los_prior - target
    nlos_error = nlos_prior - target
    overall_rmse = float(
        np.sqrt(np.mean(np.square((prediction - target)[valid], dtype=np.float64)))
    )
    los_rmse = float(np.sqrt(np.mean(np.square(los_error[los], dtype=np.float64))))
    nlos_rmse = float(np.sqrt(np.mean(np.square(nlos_error[nlos], dtype=np.float64))))

    mpl.rcParams.update({
        "font.family": "serif",
        "font.size": 7.1,
        "axes.titlesize": 7.6,
        "axes.labelsize": 7.0,
    })
    fig, axes = plt.subplots(
        3,
        2,
        figsize=(3.45, 4.82),
        constrained_layout=True,
        sharex=True,
        sharey=True,
    )
    extent = (-256, 256, -256, 256)

    attenuation_cmap = mpl.colormaps["viridis"].copy()
    attenuation_cmap.set_bad("#D9D9D9")
    rows = (
        ("All receivers", valid, target, prediction),
        ("LOS", los, target, los_prior),
        ("NLOS", nlos, target, nlos_prior),
    )
    image = None
    for row, (label, keep, truth, estimate) in enumerate(rows):
        image = axes[row, 0].imshow(
            masked(truth, keep),
            origin="lower",
            extent=extent,
            cmap=attenuation_cmap,
            vmin=75,
            vmax=145,
        )
        axes[row, 1].imshow(
            masked(estimate, keep),
            origin="lower",
            extent=extent,
            cmap=attenuation_cmap,
            vmin=75,
            vmax=145,
        )
        axes[row, 0].set_ylabel(f"{label}\ny [m]", labelpad=1)

    axes[0, 0].set_title("CKM dataset")
    axes[0, 1].set_title("Model")

    for axis in axes.flat:
        axis.set_xticks((-256, 0, 256))
        axis.set_yticks((-256, 0, 256))
        axis.tick_params(length=2, pad=1, labelbottom=True)
    axes[2, 0].set_xlabel("x [m]", labelpad=0)
    axes[2, 1].set_xlabel("x [m]", labelpad=0)
    for axis in axes[:, 1]:
        axis.tick_params(labelleft=False)

    cbar_loss = fig.colorbar(
        image,
        ax=axes,
        orientation="horizontal",
        shrink=0.82,
        pad=0.015,
        aspect=28,
    )
    cbar_loss.set_ticks((80, 110, 140))
    cbar_loss.set_label("Attenuation [dB]", labelpad=1)
    cbar_loss.ax.tick_params(length=2, pad=1)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=320, bbox_inches="tight", facecolor="white")
    print(json.dumps({
        "output": str(OUTPUT),
        "city": CITY,
        "sample": SAMPLE,
        "transmitter_height_m": h_tx,
        "topology_class": topology_class,
        "antenna_bin": antenna_bin,
        "los_pixels": int(los.sum()),
        "nlos_pixels": int(nlos.sum()),
        "overall_rmse_db": overall_rmse,
        "los_rmse_db": los_rmse,
        "nlos_rmse_db": nlos_rmse,
        "raw_nlos_rmse_db": float(np.sqrt(np.mean(np.square((raw - target)[nlos], dtype=np.float64)))),
        "coefficient_key": key,
    }, indent=2))


if __name__ == "__main__":
    main()
