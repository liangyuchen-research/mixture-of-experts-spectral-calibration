"""Plot the archived matrix-calibration results for the README.

Reads only the CSV tables under ``analysis/archived_results/`` and writes PNG/SVG
files to ``docs/figures/``. No model is run.

    python scripts/make_figures.py
"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "analysis" / "archived_results"
FIG_DIR = ROOT / "docs" / "figures"
OKABE_ITO = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9"]
IONS = ["Na", "Ca", "K", "Mg"]
METALS = ["Cu", "Ni", "Zn"]


def style() -> None:
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 9, "axes.labelsize": 9.5, "axes.titlesize": 9.5,
        "xtick.labelsize": 8.5, "ytick.labelsize": 8.5, "legend.fontsize": 8,
        "axes.linewidth": 0.7, "lines.linewidth": 1.1, "lines.markersize": 4,
        "xtick.direction": "in", "ytick.direction": "in",
        "xtick.top": True, "ytick.right": True,
        "axes.prop_cycle": mpl.cycler(color=OKABE_ITO),
        "legend.frameon": False,
        "savefig.bbox": "tight", "savefig.pad_inches": 0.03,
    })


def save(fig, name: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / f"{name}.png", dpi=200)
    plt.close(fig)
    print(f"wrote docs/figures/{name}.png")


def figure_slope_vs_matrix() -> None:
    curves = pd.read_csv(RESULTS / "per_matrix_r2" / "calibration_curves.csv")
    single_ion = curves[(curves[IONS] > 0).sum(axis=1) <= 1]
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.6), sharey=True, constrained_layout=True)
    for ax, metal in zip(axes, METALS):
        sub = single_ion[single_ion.metal == metal]
        clean = float(sub[(sub[IONS] == 0).all(axis=1)].slope.iloc[0])
        for color, ion in zip(OKABE_ITO, IONS):
            rows = sub[(sub[ion] > 0) | (sub[IONS] == 0).all(axis=1)].sort_values(ion)
            ax.plot(rows[ion], rows.slope / clean, "o-", color=color, label=f"{ion}$^{{+}}$" if ion in ("Na", "K") else f"{ion}$^{{2+}}$", ms=3.5)
        ax.axhline(1, color="0.5", lw=0.6, ls="--")
        ax.set_title(f"{metal} calibration slope", fontsize=9)
        ax.set_xlabel("Matrix ion added (ppm)")
        ax.set_xticks([0, 125, 250, 375, 500])
    axes[0].set_ylabel("Slope relative to clean water")
    axes[0].legend(loc="lower left", ncol=2, title="interfering ion", title_fontsize=8)
    for ax, tag in zip(axes, "abc"):
        ax.text(0.03, 0.96, f"({tag})", transform=ax.transAxes, fontweight="bold", va="top")
    save(fig, "calibration_slope_vs_matrix")


def figure_matched_vs_clean() -> None:
    summary = pd.read_csv(RESULTS / "matrix_matched" / "summary.csv")
    test = summary[summary.set == "testing (26 conds)"]
    preds = pd.read_csv(RESULTS / "per_matrix_r2" / "testing_predictions.csv")

    fig, (ax_bar, ax_err) = plt.subplots(1, 2, figsize=(7.4, 3.0), constrained_layout=True)
    strategies = [("clean-only", "clean-water calibration", "0.6"),
                  ("matrix-matched", "matrix-matched calibration", OKABE_ITO[0])]
    width = 0.36
    x = np.arange(len(METALS))
    for offset, (key, label, color) in zip((-width / 2, width / 2), strategies):
        values = [float(test[(test.strategy == key) & (test.metal == m)].MAE.iloc[0]) for m in METALS]
        bars = ax_bar.bar(x + offset, values, width * 0.94, color=color, label=label)
        for bar, value in zip(bars, values):
            ax_bar.text(bar.get_x() + bar.get_width() / 2, value + 0.03, f"{value:.2f}", ha="center",
                        va="bottom", fontsize=7.5)
    n = int(test.n.iloc[0])
    ax_bar.set_xticks(x, METALS)
    ax_bar.set_ylabel("Test MAE (ppm)")
    ax_bar.set_ylim(0, 2.45)
    ax_bar.legend(loc="upper center", title=f"{n} test measurements, 26 matrix conditions", title_fontsize=7.5)

    positions, data, colors = [], [], []
    for i, metal in enumerate(METALS):
        rows = preds[preds.metal == metal]
        data += [rows.err_clean.to_numpy(), rows.err_matched.to_numpy()]
        positions += [i - 0.19, i + 0.19]
        colors += ["0.6", OKABE_ITO[0]]
    boxes = ax_err.boxplot(data, positions=positions, widths=0.3, patch_artist=True, showfliers=False,
                           medianprops={"color": "k", "lw": 0.9}, whiskerprops={"lw": 0.7}, capprops={"lw": 0.7})
    for patch, color in zip(boxes["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_edgecolor("k")
        patch.set_linewidth(0.6)
    rng = np.random.default_rng(2)
    for pos, values, color in zip(positions, data, colors):
        ax_err.plot(pos + rng.normal(0, 0.045, len(values)), values, "o", ms=2, color="k", alpha=0.35, mew=0)
    ax_err.axhline(0, color="0.4", lw=0.7, ls="--")
    ax_err.set_xticks(range(len(METALS)), METALS)
    ax_err.set_ylabel("Predicted − reference (ppm)")
    ax_err.text(0.98, 0.04, "grey: clean-water calibration\nblue: matrix-matched", transform=ax_err.transAxes,
                ha="right", va="bottom", fontsize=7.5)
    for ax, tag in ((ax_bar, "(a)"), (ax_err, "(b)")):
        ax.text(0.02, 0.97, tag, transform=ax.transAxes, fontweight="bold", va="top")
    save(fig, "matrix_matched_vs_clean")


def main() -> None:
    style()
    figure_slope_vs_matrix()
    figure_matched_vs_clean()


if __name__ == "__main__":
    main()
