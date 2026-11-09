"""Measure first-passage times away from a population balanced-Lloyd saddle.

This focused follow-up was motivated by an earlier exploratory run, which
informed the choice of the 0.4 mode-amplitude threshold. The threshold was
fixed before this follow-up, but the study was not preregistered. Each
trajectory starts at the population three-center shape and uses exact
equal-capacity assignment. The stable parameter tau=0.2 is a negative
control; tau=0.5 and 0.8 have population high-mode multipliers 1.5 and 2.4.
The candidate prediction is a first-passage time with leading term
log(n)/(2 log(3*tau)) for tau>1/3, conditional on the empirical perturbation
remaining coherent near the saddle. The run records data to examine that
prediction and does not assume it is true.
"""

from __future__ import annotations

import json
import platform
import time
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

from lloyd_common import (
    generate_data,
    lloyd,
    normalized_center_shape,
    population_shape,
)


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "lloyd_finite_sample"
SEED = 20261105
TAUS = (0.2, 0.5, 0.8)
SAMPLE_SIZES = (60, 180, 540, 1620)
DATASET_REPLICATES = 40
MODE_THRESHOLD = 0.4
BOOTSTRAP_REPLICATES = 5000


def wilson_interval(successes: int, trials: int) -> tuple[float, float]:
    z = float(norm.ppf(0.975))
    proportion = successes / trials
    denominator = 1.0 + z * z / trials
    center = (proportion + z * z / (2.0 * trials)) / denominator
    radius = z * np.sqrt(
        proportion * (1.0 - proportion) / trials + z * z / (4.0 * trials * trials)
    ) / denominator
    return max(0.0, float(center - radius)), min(1.0, float(center + radius))


def summarize(group: pd.DataFrame, rng: np.random.Generator) -> dict[str, float | int]:
    hits = group.loc[group["hit_before_stabilization"], "first_hit_iteration"].to_numpy(
        dtype=float
    )
    successes = int(len(hits))
    trials = int(len(group))
    rate_low, rate_high = wilson_interval(successes, trials)

    if successes:
        bootstrap_indices = rng.integers(
            0, successes, size=(BOOTSTRAP_REPLICATES, successes)
        )
        bootstrap_medians = np.median(hits[bootstrap_indices], axis=1)
        median_hit = float(np.median(hits))
        median_low, median_high = np.quantile(bootstrap_medians, [0.025, 0.975])
        hit_q25, hit_q75 = np.quantile(hits, [0.25, 0.75])
    else:
        median_hit = float("nan")
        median_low = float("nan")
        median_high = float("nan")
        hit_q25 = float("nan")
        hit_q75 = float("nan")

    tau = float(group["tau"].iloc[0])
    n = int(group["sample_size"].iloc[0])
    multiplier = 3.0 * tau
    candidate_slope = 0.5 / np.log(multiplier) if multiplier > 1.0 else float("nan")
    return {
        "tau": tau,
        "sample_size": n,
        "datasets": trials,
        "mode_threshold": MODE_THRESHOLD,
        "population_high_mode_multiplier": multiplier,
        "hit_count": successes,
        "hit_fraction": successes / trials,
        "terminal_state_hit_count": int(group["hit_at_terminal_state"].sum()),
        "hit_fraction_wilson95_low": rate_low,
        "hit_fraction_wilson95_high": rate_high,
        "median_hit_iteration_given_hit": median_hit,
        "median_hit_bootstrap95_low": float(median_low),
        "median_hit_bootstrap95_high": float(median_high),
        "hit_iteration_q25": float(hit_q25),
        "hit_iteration_q75": float(hit_q75),
        "mean_stabilization_iteration": float(group["stabilization_iteration"].mean()),
        "candidate_log_n_slope": float(candidate_slope),
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    summary_rng = np.random.default_rng(SEED + 1)
    target = population_shape()
    target_unit = normalized_center_shape(target)
    high_mode = np.zeros_like(target_unit)
    high_mode[:, 1] = np.array([1.0, -2.0, 1.0]) / np.sqrt(6.0)

    dataset_rows: list[dict[str, float | int | bool | None]] = []
    trajectory_rows: list[dict[str, float | int]] = []
    started = time.perf_counter()

    for tau in TAUS:
        for sample_size in SAMPLE_SIZES:
            for replicate in range(DATASET_REPLICATES):
                data = generate_data(sample_size, tau, rng)
                trace: list[np.ndarray] = []
                _, _, stabilization_iteration = lloyd(data, target, trace)
                # The iteration counter is the assignment call that detects
                # the first repeated partition. The returned fixed-point
                # state is the preceding update, at index stabilization_iteration - 1.

                amplitudes = [0.0]
                for iteration, centers in enumerate(trace, start=1):
                    shape = normalized_center_shape(centers)
                    amplitude = float(np.sum((shape - target_unit) * high_mode))
                    amplitudes.append(amplitude)
                    trajectory_rows.append(
                        {
                            "tau": tau,
                            "sample_size": sample_size,
                            "replicate": replicate,
                            "iteration": iteration,
                            "high_mode_amplitude": amplitude,
                            "absolute_high_mode_amplitude": abs(amplitude),
                            "mode_threshold": MODE_THRESHOLD,
                        }
                    )

                hit_iterations = [
                    iteration
                    for iteration, amplitude in enumerate(amplitudes)
                    if iteration > 0 and abs(amplitude) >= MODE_THRESHOLD
                ]
                first_hit = hit_iterations[0] if hit_iterations else None
                dataset_rows.append(
                    {
                        "tau": tau,
                        "sample_size": sample_size,
                        "replicate": replicate,
                        "first_update_mode_amplitude": amplitudes[1],
                        "first_hit_iteration": first_hit,
                        # Keep first passage at the terminal fixed point
                        # distinct from a strict preterminal hit.
                        "hit_before_stabilization": (
                            first_hit is not None
                            and first_hit < stabilization_iteration - 1
                        ),
                        "hit_at_terminal_state": (
                            first_hit is not None
                            and first_hit == stabilization_iteration - 1
                        ),
                        "stabilization_iteration": stabilization_iteration,
                        "terminal_mode_amplitude": amplitudes[-1],
                    }
                )

    datasets = pd.DataFrame(dataset_rows)
    trajectories = pd.DataFrame(trajectory_rows)
    datasets.to_csv(RESULTS / "escape_time_by_dataset.csv", index=False)
    trajectories.to_csv(RESULTS / "escape_time_trajectories.csv", index=False)

    summary_rows = [
        summarize(group, summary_rng)
        for _, group in datasets.groupby(["tau", "sample_size"], sort=True)
    ]
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(RESULTS / "escape_time_summary.csv", index=False)

    elapsed = time.perf_counter() - started
    metadata = {
        "experiment": "first-passage dynamics from a population balanced-Lloyd saddle",
        "protocol": {
            "threshold_fixed_before_followup": MODE_THRESHOLD,
            "threshold_selection_history": (
                "The threshold was informed by an earlier exploratory run and fixed "
                "before this follow-up; the study was not preregistered."
            ),
            "taus": list(TAUS),
            "sample_sizes": list(SAMPLE_SIZES),
            "independent_datasets_per_condition": DATASET_REPLICATES,
            "dataset_bootstrap_replicates": BOOTSTRAP_REPLICATES,
            "seed": SEED,
            "assignment": "exact equal-capacity linear assignment using scipy.optimize.linear_sum_assignment",
            "initialization": "population three-center fixed shape",
            "stopping": "unchanged exact partition on consecutive assignments; maximum 100 iterations",
            "event": "absolute normalized (1,-2,1)/sqrt(6) high-mode amplitude first reaches 0.4 strictly before the returned terminal fixed-point state; the repeat-detection assignment call is one index later than that state",
            "candidate_prediction": "for tau>1/3, first-passage iteration has leading term log(n)/(2*log(3*tau)) if the empirical perturbation remains coherent near the saddle; this is a hypothesis under study",
            "uncertainty": "Wilson 95% intervals for hit fractions; percentile intervals from 5,000 dataset bootstrap resamples for median hit time conditional on a hit",
        },
        "software": {
            "python": platform.python_version(),
            "numpy": version("numpy"),
            "scipy": version("scipy"),
            "pandas": version("pandas"),
        },
        "runtime_seconds": elapsed,
        "outputs": [
            "results/lloyd_finite_sample/escape_time_by_dataset.csv",
            "results/lloyd_finite_sample/escape_time_trajectories.csv",
            "results/lloyd_finite_sample/escape_time_summary.csv",
        ],
    }
    with (RESULTS / "escape_time_metadata.json").open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(summary.to_string(index=False, float_format=lambda value: f"{value:.3f}"))
    print(f"runtime_seconds={elapsed:.1f}")


if __name__ == "__main__":
    main()
