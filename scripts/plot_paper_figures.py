"""Recreate the paper's two experimental figures from the saved summary CSV."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "results" / "lloyd_finite_sample" / "escape_time_summary.csv"
FIGURES = ROOT / "figures" / "lloyd_finite_sample"
COLORS = {0.2: "#0072B2", 0.5: "#D55E00", 0.8: "#009E73"}
MARKERS = {0.2: "o", 0.5: "s", 0.8: "^"}
N_TICKS = [60, 180, 540, 1620]

matplotlib.rcParams.update({
    "font.family": "Microsoft YaHei",
    "font.size": 9,
    "axes.labelsize": 9,
    "legend.fontsize": 8,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.16,
    "grid.linewidth": 0.6,
    "lines.linewidth": 1.5,
    "lines.markersize": 5,
    "svg.fonttype": "none",
})


def read_rows() -> list[dict[str, float | int | None]]:
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as stream:
        raw = list(csv.DictReader(stream))
    rows = []
    for row in raw:
        rows.append({
            "tau": float(row["tau"]),
            "n": int(row["sample_size"]),
            "fraction": float(row["hit_fraction"]),
            "wilson_low": float(row["hit_fraction_wilson95_low"]),
            "wilson_high": float(row["hit_fraction_wilson95_high"]),
            "median": float(row["median_hit_iteration_given_hit"])
            if row["median_hit_iteration_given_hit"].strip() else None,
            "boot_low": float(row["median_hit_bootstrap95_low"])
            if row["median_hit_bootstrap95_low"].strip() else None,
            "boot_high": float(row["median_hit_bootstrap95_high"])
            if row["median_hit_bootstrap95_high"].strip() else None,
        })
    if len(rows) != 12 or sum(row["median"] is not None for row in rows) != 9:
        raise ValueError("Expected 12 existing rows and 9 observed conditional medians")
    return rows


def setup_axes(ax, ylabel: str) -> None:
    ax.set_xscale("log")
    ax.set_xticks(N_TICKS, labels=["60", "180", "540", "1620"])
    ax.set_xlabel("样本量 $n$（对数坐标）")
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", color="#BFC5C9")
    ax.tick_params(labelsize=8)


def save_pair(fig, output: Path, stem: str) -> None:
    output.mkdir(parents=True, exist_ok=True)
    fig.savefig(output / f"{stem}.png", facecolor="white")
    fig.savefig(output / f"{stem}.svg", facecolor="white")
    plt.close(fig)


def figure_hit_fraction(rows, width: float, output: Path) -> None:
    # Keep the original 3.4-inch plot height; narrow only the canvas width.
    fig, ax = plt.subplots(figsize=(width, 3.4))
    for tau in (0.2, 0.5, 0.8):
        selected = sorted((row for row in rows if row["tau"] == tau),
                          key=lambda row: row["n"])
        x = np.array([row["n"] for row in selected], dtype=float)
        y = np.array([row["fraction"] for row in selected], dtype=float)
        low = np.array([row["wilson_low"] for row in selected], dtype=float)
        high = np.array([row["wilson_high"] for row in selected], dtype=float)
        x_plot = x.copy()
        if tau == 0.5:
            x_plot[-1] *= 0.96
        elif tau == 0.8:
            x_plot[-1] *= 1.04
        ax.plot(x_plot, y, color=COLORS[tau], zorder=3)
        ax.scatter(x_plot, y, color=COLORS[tau], marker=MARKERS[tau],
                   s=48, zorder=4)
        ax.errorbar(x_plot, y, yerr=np.vstack((y - low, high - y)), fmt="none",
                    ecolor=COLORS[tau], elinewidth=1.0, capsize=3, zorder=2)
    handles = [Line2D([0], [0], color=COLORS[tau], marker=MARKERS[tau],
                      linewidth=1.7, markersize=6, label=fr"$\tau={tau}$")
               for tau in (0.2, 0.5, 0.8)]
    setup_axes(ax, "严格终态前阈值命中比例")
    ax.set_ylim(0, 1.04)
    ax.set_yticks(np.linspace(0, 1, 6))
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 1.20),
              ncol=3, frameon=False, handlelength=1.8, columnspacing=1.6)
    fig.subplots_adjust(left=0.17, right=0.97, top=0.80, bottom=0.18)
    save_pair(fig, output, "fig03_empirical_hit_fraction")


def figure_conditional_iterations(rows, width: float, output: Path) -> None:
    # Keep the original 3.05-inch plot height; retain only observed medians.
    fig, ax = plt.subplots(figsize=(width, 3.05))
    for tau in (0.2, 0.5, 0.8):
        selected = sorted(
            (row for row in rows if row["tau"] == tau and row["median"] is not None),
            key=lambda row: row["n"],
        )
        if not selected:
            continue
        x_true = np.array([row["n"] for row in selected], dtype=float)
        x_plot = x_true.copy()
        for index, n in enumerate(x_true):
            if n == 60 and tau == 0.5:
                x_plot[index] = n * 0.96
            elif n == 60 and tau == 0.8:
                x_plot[index] = n * 1.04
        y = np.array([row["median"] for row in selected], dtype=float)
        low = np.array([row["boot_low"] for row in selected], dtype=float)
        high = np.array([row["boot_high"] for row in selected], dtype=float)
        ax.plot(x_plot, y, color=COLORS[tau], marker=MARKERS[tau],
                label=fr"$\tau={tau}$", zorder=3)
        ax.errorbar(x_plot, y, yerr=np.vstack((y - low, high - y)), fmt="none",
                    ecolor=COLORS[tau], elinewidth=1.0, capsize=3, zorder=2)
    setup_axes(ax, "命中条件下的中位迭代步数")
    ax.set_ylim(0, 12)
    ax.set_yticks(np.arange(0, 13, 2))
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.14),
              ncol=3, frameon=False, handlelength=1.8, columnspacing=1.6)
    fig.text(0.5, 0.025,
             "n=60 处 $\\tau=0.5$ 和 $\\tau=0.8$ 的标记仅为显示而横向错开；真实样本量均为60。",
             ha="center", fontsize=7.2, color="#444444")
    fig.subplots_adjust(left=0.17, right=0.97, top=0.82, bottom=0.24)
    save_pair(fig, output, "fig04_conditional_hit_iterations")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=float, default=4.75,
                        help="canvas width in inches; source figure height remains unchanged")
    parser.add_argument("--output-dir", type=Path, default=FIGURES)
    args = parser.parse_args()
    if args.width <= 0:
        raise ValueError("Figure width must be positive")
    rows = read_rows()
    figure_hit_fraction(rows, args.width, args.output_dir)
    figure_conditional_iterations(rows, args.width, args.output_dir)
    print(f"Read {len(rows)} existing rows; emitted 12 hit-rate points and 9 conditional medians.")
    print(f"Output: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
