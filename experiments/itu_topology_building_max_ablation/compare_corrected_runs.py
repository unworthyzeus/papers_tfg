"""Compare both building-maximum ITU 3 runs by topology."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, Mapping, Sequence


EXPERIMENT_ROOT = Path(__file__).resolve().parent
DEFAULT_PREVIOUS = (
    EXPERIMENT_ROOT
    / "results"
    / "two_ray_itu3_building_max"
    / "official_test_per_map_metrics.csv"
)
DEFAULT_CURRENT = (
    EXPERIMENT_ROOT
    / "results"
    / "radial_only_itu3_building_max"
    / "official_test_per_map_metrics.csv"
)
REGIONS = ("overall", "los", "nlos")


def _load_rows(path: Path) -> Dict[tuple[str, str], Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return {(row["city"], row["sample"]): row for row in rows}


def _aggregate(
    rows: Sequence[Mapping[str, str]],
    experiment: str,
) -> list[Dict[str, object]]:
    accum = defaultdict(
        lambda: {
            "maps": 0,
            **{
                f"{region}_{name}": 0.0
                for region in REGIONS
                for name in ("pixels", "sse", "sae")
            },
        }
    )
    for row in rows:
        topology = row["topology_class"]
        item = accum[topology]
        item["maps"] += 1
        for region in REGIONS:
            pixels = float(row[f"{region}_pixels"])
            rmse = float(row[f"{region}_rmse_db"])
            mae = float(row[f"{region}_mae_db"])
            if pixels <= 0.0:
                continue
            if not math.isfinite(rmse) or not math.isfinite(mae):
                raise RuntimeError(
                    f"non-finite {region} metric with {pixels:g} pixels for "
                    f"{row['city']}/{row['sample']}"
                )
            item[f"{region}_pixels"] += pixels
            item[f"{region}_sse"] += pixels * rmse**2
            item[f"{region}_sae"] += pixels * mae

    output = []
    for topology in sorted(accum):
        item = accum[topology]
        result: Dict[str, object] = {
            "experiment": experiment,
            "topology": topology,
            "maps": int(item["maps"]),
        }
        for region in REGIONS:
            pixels = float(item[f"{region}_pixels"])
            result[f"{region}_pixels"] = int(pixels)
            result[f"{region}_rmse_db"] = (
                math.sqrt(float(item[f"{region}_sse"]) / pixels)
                if pixels
                else float("nan")
            )
            result[f"{region}_mae_db"] = (
                float(item[f"{region}_sae"]) / pixels
                if pixels
                else float("nan")
            )
        output.append(result)
    return output


def _write_csv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    rows = list(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous", type=Path, default=DEFAULT_PREVIOUS)
    parser.add_argument("--current", type=Path, default=DEFAULT_CURRENT)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=EXPERIMENT_ROOT / "results" / "topology_comparison",
    )
    args = parser.parse_args()

    previous = _load_rows(args.previous)
    current = _load_rows(args.current)
    if previous.keys() != current.keys():
        raise RuntimeError("the two runs do not contain the same test samples")
    topology_mismatches = [
        key
        for key in previous
        if previous[key]["topology_class"] != current[key]["topology_class"]
    ]
    if topology_mismatches:
        raise RuntimeError(
            f"topology assignments differ for {len(topology_mismatches)} test samples"
        )

    previous_agg = _aggregate(
        list(previous.values()), "two_ray_plus_r_itu3_building_max"
    )
    current_agg = _aggregate(
        list(current.values()), "fspl_plus_refitted_r_itu3_building_max"
    )
    by_previous = {row["topology"]: row for row in previous_agg}
    by_current = {row["topology"]: row for row in current_agg}
    if by_previous.keys() != by_current.keys():
        raise RuntimeError("the two runs do not contain the same topology groups")

    comparison = []
    for topology in sorted(by_previous):
        old = by_previous[topology]
        new = by_current[topology]
        row: Dict[str, object] = {
            "topology": topology,
            "maps": old["maps"],
        }
        for region in REGIONS:
            old_value = float(old[f"{region}_rmse_db"])
            new_value = float(new[f"{region}_rmse_db"])
            row[f"{region}_rmse_two_ray_plus_r_db"] = old_value
            row[f"{region}_rmse_fspl_plus_refitted_r_db"] = new_value
            row[f"{region}_rmse_delta_db"] = new_value - old_value
        comparison.append(row)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(args.out_dir / "rmse_by_topology_both_runs.csv", previous_agg + current_agg)
    _write_csv(args.out_dir / "rmse_by_topology_comparison.csv", comparison)
    payload = {
        "previous": str(args.previous),
        "current": str(args.current),
        "aggregation": "pixel-weighted from per-map SSE, building pixels excluded",
        "same_test_samples": True,
        "same_topology_assignment": True,
        "results": comparison,
    }
    (args.out_dir / "rmse_by_topology_comparison.json").write_text(
        json.dumps(payload, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
