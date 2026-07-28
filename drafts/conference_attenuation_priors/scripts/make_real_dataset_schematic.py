#!/usr/bin/env python3
"""Build the CKM dataset schematic from one real HDF5 sample.

The figure contains the six spatial arrays stored for each labeled sample and
shows UAV height separately because it is a scalar rather than a raster. No
channel values are synthesized.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import h5py
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Circle, Polygon, Rectangle


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "figures" / "ckm_dataset_real_sample.png"
mpl.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hdf5", type=Path, required=True)
    parser.add_argument("--city", default="Barcelona")
    parser.add_argument("--sample", default="sample_02806")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dpi", type=int, default=300)
    return parser.parse_args()


def scalar_text(dataset: h5py.Dataset) -> str:
    value = np.asarray(dataset[()]).reshape(-1)[0]
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return str(value)


def load_sample(path: Path, city: str, sample: str) -> dict[str, object]:
    with h5py.File(path, "r") as handle:
        group = handle[city][sample]
        return {
            "topology_map": np.asarray(group["topology_map"][...], dtype=np.float32),
            "building_mask": np.asarray(group["building_mask"][...], dtype=np.uint8),
            "los_mask": np.asarray(group["los_mask"][...], dtype=np.uint8),
            "path_loss": np.asarray(group["path_loss"][...], dtype=np.float32),
            "delay_spread": np.asarray(group["delay_spread"][...], dtype=np.float32),
            "angular_spread": np.asarray(group["angular_spread"][...], dtype=np.float32),
            "uav_height": float(np.asarray(group["uav_height"][...]).reshape(-1)[0]),
            "topology_3_class": scalar_text(group["topology_3_class"]),
            "topology_6_class": scalar_text(group["topology_6_class"]),
        }


def draw_building(ax: plt.Axes, x: float, y: float, w: float, h: float) -> None:
    depth = 0.055
    top = Polygon(
        [(x, y + h), (x + depth, y + h + depth), (x + w + depth, y + h + depth), (x + w, y + h)],
        closed=True,
        facecolor="#d9e8f3",
        edgecolor="#31475b",
        linewidth=0.8,
    )
    front = Rectangle((x, y), w, h, facecolor="#edf4f8", edgecolor="#31475b", linewidth=0.8)
    side = Polygon(
        [(x + w, y), (x + w + depth, y + depth), (x + w + depth, y + h + depth), (x + w, y + h)],
        closed=True,
        facecolor="#b8d4e7",
        edgecolor="#31475b",
        linewidth=0.8,
    )
    ax.add_patch(front)
    ax.add_patch(side)
    ax.add_patch(top)
    cols = max(1, int(w / 0.045))
    rows = max(1, int(h / 0.07))
    for row in range(rows):
        for col in range(cols):
            wx = x + 0.025 + col * max(0.036, (w - 0.05) / cols)
            wy = y + 0.025 + row * max(0.055, (h - 0.05) / rows)
            ax.add_patch(Rectangle((wx, wy), 0.015, 0.023, facecolor="#4f86b5", edgecolor="none"))


def draw_drone(ax: plt.Axes, cx: float, cy: float) -> None:
    color = "#1f2933"
    ax.add_patch(Rectangle((cx - 0.035, cy - 0.015), 0.07, 0.03, facecolor="white", edgecolor=color, lw=1.0))
    for dx, dy in [(-0.065, 0.03), (0.065, 0.03), (-0.065, -0.03), (0.065, -0.03)]:
        ax.plot([cx, cx + dx], [cy, cy + dy], color=color, lw=1.0)
        ax.add_patch(Circle((cx + dx, cy + dy), 0.027, fill=False, edgecolor=color, lw=1.0))
    ax.plot([cx, cx], [cy - 0.015, cy - 0.04], color=color, lw=1.0)


def draw_context(ax: plt.Axes, data: dict[str, object], city: str, sample: str) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.5, 0.965, "ONE DATASET SAMPLE", ha="center", va="top", fontsize=12, fontweight="bold")
    ax.text(0.5, 0.918, f"{city} · {sample.replace('_', ' ')}", ha="center", va="top", fontsize=8.2, color="#4b5563")

    plane = np.array([[0.08, 0.30], [0.83, 0.30], [0.96, 0.56], [0.21, 0.56]])
    ax.add_patch(Polygon(plane, closed=True, facecolor="#fbfcfd", edgecolor="#52606d", linewidth=0.9))
    for fraction in np.linspace(0.12, 0.88, 7):
        a = plane[0] * (1 - fraction) + plane[3] * fraction
        b = plane[1] * (1 - fraction) + plane[2] * fraction
        ax.plot([a[0], b[0]], [a[1], b[1]], color="#c8d0d7", lw=0.45)
    for fraction in np.linspace(0.08, 0.92, 8):
        a = plane[0] * (1 - fraction) + plane[1] * fraction
        b = plane[3] * (1 - fraction) + plane[2] * fraction
        ax.plot([a[0], b[0]], [a[1], b[1]], color="#c8d0d7", lw=0.45)

    draw_building(ax, 0.17, 0.40, 0.13, 0.13)
    draw_building(ax, 0.35, 0.36, 0.10, 0.20)
    draw_building(ax, 0.55, 0.39, 0.12, 0.11)
    draw_building(ax, 0.73, 0.38, 0.11, 0.24)

    drone_x, drone_y = 0.53, 0.77
    draw_drone(ax, drone_x, drone_y)
    ray_targets = [(0.15, 0.33), (0.38, 0.34), (0.58, 0.34), (0.85, 0.35)]
    for target_x, target_y in ray_targets:
        ax.plot([drone_x, target_x], [drone_y - 0.04, target_y], color="#b4534b", lw=0.7, alpha=0.75)
        ax.add_patch(Circle((target_x, target_y), 0.008, color="#1f2933"))

    h_tx = float(data["uav_height"])
    ax.annotate(
        "",
        xy=(0.91, drone_y),
        xytext=(0.91, 0.315),
        arrowprops={"arrowstyle": "<->", "color": "#1f2933", "lw": 0.9},
    )
    ax.text(0.925, 0.54, rf"$h_{{\mathrm{{Tx}}}}={h_tx:.1f}$ m", rotation=90, ha="left", va="center", fontsize=8.3)

    layer_base = np.array([[0.14, 0.12], [0.82, 0.12], [0.91, 0.20], [0.23, 0.20]])
    for layer in range(6):
        offset = layer * 0.018
        poly = layer_base + np.array([0.0, offset])
        ax.add_patch(Polygon(poly, closed=True, facecolor="white", edgecolor="#1f2933", linewidth=0.8))
    ax.text(0.52, 0.075, "6 aligned 513 × 513 rasters", ha="center", va="center", fontsize=8.4)

    ax.text(
        0.5,
        0.018,
        "3-class: " + str(data["topology_3_class"]).replace("_", "/")
        + "   ·   6-class: " + str(data["topology_6_class"]).replace("_", "/"),
        ha="center",
        va="bottom",
        fontsize=7.2,
        color="#4b5563",
    )


def finite_limits(values: np.ndarray, valid_mask: np.ndarray, low: float, high: float) -> tuple[float, float]:
    valid = values[(valid_mask > 0) & np.isfinite(values)]
    if valid.size == 0:
        return 0.0, 1.0
    lo, hi = np.percentile(valid, [low, high])
    if hi <= lo:
        hi = lo + 1.0
    return float(lo), float(hi)


def add_panel(
    ax: plt.Axes,
    values: np.ndarray,
    title: str,
    cmap: mpl.colors.Colormap | str,
    *,
    vmin: float | None = None,
    vmax: float | None = None,
    invalid_mask: np.ndarray | None = None,
    continuous: bool = False,
) -> None:
    shown = np.array(values, dtype=np.float32, copy=True)
    cmap_obj = mpl.colormaps.get_cmap(cmap) if isinstance(cmap, str) else cmap
    cmap_obj = cmap_obj.copy()
    if invalid_mask is not None:
        shown = np.ma.masked_where(invalid_mask > 0, shown)
        cmap_obj.set_bad("#d8d8d8")
    image = ax.imshow(shown, cmap=cmap_obj, origin="lower", extent=(-256, 256, -256, 256), vmin=vmin, vmax=vmax)
    ax.plot(0, 0, marker="+", markersize=4.8, markeredgewidth=0.9, color="black")
    ax.set_title(title, fontsize=8.5, pad=3.0, fontweight="semibold")
    ax.set_xticks([-256, 0, 256])
    ax.set_yticks([-256, 0, 256])
    ax.tick_params(axis="both", labelsize=5.4, length=1.7, pad=1.0)
    for spine in ax.spines.values():
        spine.set_linewidth(0.65)
        spine.set_color("#2f3b45")
    if continuous:
        bar = ax.inset_axes([0.12, -0.155, 0.76, 0.045])
        cbar = plt.colorbar(image, cax=bar, orientation="horizontal")
        cbar.set_ticks([vmin, vmax])
        cbar.ax.tick_params(labelsize=5.2, length=1.4, pad=1.0)
        cbar.outline.set_linewidth(0.45)


def build_figure(data: dict[str, object], city: str, sample: str) -> plt.Figure:
    fig = plt.figure(figsize=(15.0, 5.0), facecolor="white")
    outer = fig.add_gridspec(1, 2, width_ratios=[1.00, 1.85], wspace=0.05)
    context_ax = fig.add_subplot(outer[0, 0])
    draw_context(context_ax, data, city, sample)

    right = outer[0, 1].subgridspec(2, 3, wspace=0.20, hspace=0.38)
    axes = [fig.add_subplot(right[row, col]) for row in range(2) for col in range(3)]
    building = np.asarray(data["building_mask"])
    topology = np.asarray(data["topology_map"])
    path_loss = np.asarray(data["path_loss"])
    delay = np.asarray(data["delay_spread"])
    angular = np.asarray(data["angular_spread"])
    valid_mask = ((building == 0) & np.isfinite(path_loss) & (path_loss >= 20.0)).astype(np.uint8)
    # The gray overlay has one meaning only: the receiver lies on a building.
    # Other unavailable channel targets remain distinct from the building mask.
    building_pixel_mask = building

    height_max = max(1.0, float(np.ceil(np.nanmax(topology) / 10.0) * 10.0))
    pl_min, pl_max = finite_limits(path_loss, valid_mask, 1.0, 99.0)
    ds_min, ds_max = finite_limits(delay, valid_mask, 0.0, 99.5)
    as_min, as_max = finite_limits(angular, valid_mask, 0.0, 99.5)

    add_panel(axes[0], topology, "Building height [m]", "cividis", vmin=0.0, vmax=height_max, continuous=True)
    add_panel(
        axes[1],
        building,
        "Building mask",
        ListedColormap(["#f4f6f7", "#315f7d"]),
        vmin=0.0,
        vmax=1.0,
    )
    add_panel(
        axes[2],
        np.asarray(data["los_mask"]),
        "LoS mask",
        ListedColormap(["#f2f2f2", "#3d83ad"]),
        vmin=0.0,
        vmax=1.0,
    )
    add_panel(
        axes[3],
        path_loss,
        "Att. (PL) [dB]",
        "magma",
        vmin=pl_min,
        vmax=pl_max,
        invalid_mask=building_pixel_mask,
        continuous=True,
    )
    add_panel(
        axes[4],
        delay,
        "Delay spread [ns]",
        "viridis",
        vmin=ds_min,
        vmax=ds_max,
        invalid_mask=building_pixel_mask,
        continuous=True,
    )
    add_panel(
        axes[5],
        angular,
        "Angular spread [deg]",
        "plasma",
        vmin=as_min,
        vmax=as_max,
        invalid_mask=building_pixel_mask,
        continuous=True,
    )

    fig.text(
        0.70,
        0.017,
        "Crosses mark the central transmitter pixel; gray pixels denote buildings, not excluded ground receivers. Building pixels are excluded from the metrics.",
        ha="center",
        va="bottom",
        fontsize=7.4,
        color="#4b5563",
    )
    return fig


def main() -> None:
    args = parse_args()
    data = load_sample(args.hdf5, args.city, args.sample)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    figure = build_figure(data, args.city, args.sample)
    figure.savefig(output, dpi=args.dpi, bbox_inches="tight", pad_inches=0.04)
    pdf_output = output.with_suffix(".pdf")
    figure.savefig(pdf_output, bbox_inches="tight", pad_inches=0.04)
    plt.close(figure)
    print(output)
    print(pdf_output)


if __name__ == "__main__":
    main()
