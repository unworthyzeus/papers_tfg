"""Compare the isolated ITU routing result with the official paper baseline."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict


EXPERIMENT_ROOT = Path(__file__).resolve().parent
PAPERS_ROOT = EXPERIMENT_ROOT.parents[1]
DEFAULT_BASELINE = (
    PAPERS_ROOT
    / "drafts"
    / "conference_attenuation_priors"
    / "data"
    / "official_split_analysis"
    / "official_test_summary.json"
)


def _load_metrics(path: Path) -> Dict[str, float]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    metrics = payload["final_variant"]["test_metrics"]
    return {
        "overall_rmse_db": float(metrics["overall_rmse_db"]),
        "los_rmse_db": float(metrics["los_rmse_db"]),
        "nlos_rmse_db": float(metrics["nlos_rmse_db"]),
        "overall_mae_db": float(metrics["overall_mae_db"]),
        "nlos_mae_db": float(metrics["nlos_mae_db"]),
    }


def _load_city_metrics(path: Path) -> Dict[str, Dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {
            row["city"]: {
                key: float(row[key])
                for key in (
                    "overall_rmse_db",
                    "nlos_rmse_db",
                    "overall_mae_db",
                    "nlos_mae_db",
                )
            }
            for row in csv.DictReader(handle)
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument(
        "--candidate",
        type=Path,
        default=EXPERIMENT_ROOT / "results" / "itu3" / "official_test_summary.json",
    )
    parser.add_argument(
        "--out-dir", type=Path, default=EXPERIMENT_ROOT / "results" / "comparison"
    )
    args = parser.parse_args()

    baseline = _load_metrics(args.baseline)
    candidate = _load_metrics(args.candidate)
    rows = []
    for metric in baseline:
        rows.append(
            {
                "metric": metric,
                "official_current": baseline[metric],
                "itu_candidate": candidate[metric],
                "itu_minus_current": candidate[metric] - baseline[metric],
            }
        )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    with (args.out_dir / "comparison.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    baseline_city = _load_city_metrics(
        args.baseline.parent / "official_test_per_city_metrics.csv"
    )
    candidate_city = _load_city_metrics(
        args.candidate.parent / "official_test_per_city_metrics.csv"
    )
    if baseline_city.keys() != candidate_city.keys():
        raise RuntimeError("baseline and candidate test city sets do not match")
    city_rows = []
    for city in sorted(baseline_city):
        row: Dict[str, str | float] = {"city": city}
        for metric in baseline_city[city]:
            row[f"{metric}_current"] = baseline_city[city][metric]
            row[f"{metric}_itu3"] = candidate_city[city][metric]
            row[f"{metric}_delta"] = (
                candidate_city[city][metric] - baseline_city[city][metric]
            )
        city_rows.append(row)
    with (args.out_dir / "per_city_comparison.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(city_rows[0]))
        writer.writeheader()
        writer.writerows(city_rows)
    city_summary = {}
    for metric in baseline_city[next(iter(baseline_city))]:
        deltas = [float(row[f"{metric}_delta"]) for row in city_rows]
        city_summary[metric] = {
            "improved_cities": sum(delta < 0.0 for delta in deltas),
            "worsened_cities": sum(delta > 0.0 for delta in deltas),
            "equal_cities": sum(delta == 0.0 for delta in deltas),
            "mean_city_delta": sum(deltas) / len(deltas),
        }
    comparison = {
        "baseline": str(args.baseline),
        "candidate": str(args.candidate),
        "metrics": rows,
        "per_city_summary": city_summary,
    }
    (args.out_dir / "comparison.json").write_text(
        json.dumps(comparison, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(comparison, indent=2))


if __name__ == "__main__":
    main()
