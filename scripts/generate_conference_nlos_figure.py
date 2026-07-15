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
from matplotlib.colors import BoundaryNorm, ListedColormap

from run_conference_attenuation_ablation import compute_cost231_map


REPO_ROOT = Path(__file__).resolve().parents[1]
HDF5_PATH = Path(r"C:\TFG\TFGpractice\Datasets\CKM_Dataset_270326.h5")
REFERENCE_DIR = Path(r"C:\TFG\TFGpractice\TFGEightiethTry80\scripts\recalibrate_priors")
CALIBRATION = REPO_ROOT / "drafts" / "conference_attenuation_priors" / "data" / "official_split_analysis" / "nlos_regime_calibration_official.json"
LOS_CALIBRATION = Path(r"C:\TFG\TFGpractice\TFGSeventyEighthTry78\hybrid_out_try80_split\calibrations\try78_los_two_ray_calibration_try80split.json")
OUTPUT = REPO_ROOT / "drafts" / "conference_attenuation_priors" / "figures" / "nlos_heldout_example.png"
CITY = "Vancouver"
SAMPLE = "sample_15262"


def masked(values: np.ndarray, keep: np.ndarray) -> np.ma.MaskedArray:
    return np.ma.array(values, mask=~keep)


def main() -> None:
    sys.path.insert(0, str(REFERENCE_DIR))
    import try78_hybrid_path_loss_reference as priors
    import try78_los_path_loss_prior as los_model

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
    los_error = los_prior - target
    nlos_error = nlos_prior - target
    los_rmse = float(np.sqrt(np.mean(np.square(los_error[los], dtype=np.float64))))
    nlos_rmse = float(np.sqrt(np.mean(np.square(nlos_error[nlos], dtype=np.float64))))

    mpl.rcParams.update({
        "font.family": "serif",
        "font.size": 7.0,
        "axes.titlesize": 7.4,
        "axes.labelsize": 6.8,
    })
    fig, axes = plt.subplots(2, 4, figsize=(7.12, 3.72), constrained_layout=True)
    extent = (-256, 256, -256, 256)

    classes = np.full(topology.shape, 2, dtype=np.uint8)
    classes[los] = 0
    classes[nlos] = 1
    support_cmap = ListedColormap(("#4C78A8", "#F58518", "#4A4A4A"))
    support_norm = BoundaryNorm((-0.5, 0.5, 1.5, 2.5), support_cmap.N)
    axes[0, 0].imshow(classes, origin="lower", extent=extent, cmap=support_cmap, norm=support_norm)
    axes[0, 0].set_title("(a) Support\nLoS / NLoS / buildings")

    attenuation_cmap = mpl.colormaps["viridis"].copy()
    attenuation_cmap.set_bad("#E6E6E6")
    im_target = axes[0, 1].imshow(
        masked(target, los), origin="lower", extent=extent,
        cmap=attenuation_cmap, vmin=75, vmax=145,
    )
    axes[0, 1].set_title("(b) LoS target [dB]")
    axes[0, 2].imshow(
        masked(los_prior, los), origin="lower", extent=extent,
        cmap=attenuation_cmap, vmin=75, vmax=145,
    )
    axes[0, 2].set_title("(c) LoS prior [dB]")

    error_cmap = mpl.colormaps["RdBu_r"].copy()
    error_cmap.set_bad("#E6E6E6")
    im_error = axes[0, 3].imshow(
        masked(los_error, los), origin="lower", extent=extent,
        cmap=error_cmap, vmin=-12, vmax=12,
    )
    axes[0, 3].set_title(f"(d) LoS prior - target [dB]\nRMSE {los_rmse:.2f} dB")

    axes[1, 0].imshow(
        masked(raw, nlos), origin="lower", extent=extent,
        cmap=attenuation_cmap, vmin=75, vmax=145,
    )
    axes[1, 0].set_title(r"(e) COST231 term $\mathrm{PL}_{C}$ [dB]")

    axes[1, 1].imshow(
        masked(target, nlos), origin="lower", extent=extent,
        cmap=attenuation_cmap, vmin=75, vmax=145,
    )
    axes[1, 1].set_title("(f) NLoS target [dB]")
    axes[1, 2].imshow(
        masked(nlos_prior, nlos), origin="lower", extent=extent,
        cmap=attenuation_cmap, vmin=75, vmax=145,
    )
    axes[1, 2].set_title("(g) NLoS prior [dB]")
    axes[1, 3].imshow(
        masked(nlos_error, nlos), origin="lower", extent=extent,
        cmap=error_cmap, vmin=-12, vmax=12,
    )
    axes[1, 3].set_title(f"(h) NLoS prior - target [dB]\nRMSE {nlos_rmse:.2f} dB")

    for axis in axes.flat:
        axis.set_xticks((-200, 0, 200))
        axis.set_yticks((-200, 0, 200))
        axis.tick_params(length=2, pad=1)
        axis.set_xlabel("x [m]", labelpad=0)
    axes[0, 0].set_ylabel("y [m]", labelpad=0)
    axes[1, 0].set_ylabel("y [m]", labelpad=0)
    for axis in axes[:, 1:].flat:
        axis.set_yticklabels([])

    cbar_loss = fig.colorbar(
        im_target,
        ax=(axes[0, 1], axes[0, 2], axes[1, 0], axes[1, 1], axes[1, 2]),
        orientation="horizontal", shrink=0.78, pad=0.03,
    )
    cbar_loss.set_ticks((80, 110, 140))
    cbar_loss.ax.tick_params(length=2, pad=1)
    cbar_error = fig.colorbar(
        im_error, ax=(axes[0, 3], axes[1, 3]),
        orientation="horizontal", shrink=0.86, pad=0.03,
    )
    cbar_error.set_ticks((-10, 0, 10))
    cbar_error.ax.tick_params(length=2, pad=1)

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
        "los_rmse_db": los_rmse,
        "nlos_rmse_db": nlos_rmse,
        "raw_nlos_rmse_db": float(np.sqrt(np.mean(np.square((raw - target)[nlos], dtype=np.float64)))),
        "coefficient_key": key,
    }, indent=2))


if __name__ == "__main__":
    main()
