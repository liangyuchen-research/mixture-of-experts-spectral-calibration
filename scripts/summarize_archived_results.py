"""Summarize stored model-error columns without rerunning the spectral model."""

import argparse
import csv
import math
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]


def summarize(path):
    """Return MAE, signed bias, and RMSE from each metal's archived error column."""
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    summaries = []
    for metal in ("Cu", "Ni", "Zn"):
        field = f"{metal}_model_err"
        values = [float(row[field]) for row in rows]
        if not values or not all(math.isfinite(value) for value in values):
            raise ValueError(f"Empty or nonfinite archived error column: {path.name}/{field}")
        summaries.append({
            "table": path.stem, "metal": metal, "n": len(values),
            "MAE_ppm": statistics.fmean(abs(value) for value in values),
            "bias_ppm": statistics.fmean(values),
            "RMSE_ppm": math.sqrt(statistics.fmean(value * value for value in values)),
            "provenance": "archived_rounded_error_column",
        })
    return summaries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=ROOT / "analysis/archived_results/model_v6")
    args = parser.parse_args()
    tables = sorted(args.directory.glob("*_stage*.csv"))
    if not tables:
        parser.error("No archived stage-result tables found.")
    writer = csv.DictWriter(sys.stdout, fieldnames=["table", "metal", "n", "MAE_ppm", "bias_ppm", "RMSE_ppm", "provenance"], lineterminator="\n")
    writer.writeheader()
    for table in tables:
        writer.writerows(summarize(table))


if __name__ == "__main__":
    main()
