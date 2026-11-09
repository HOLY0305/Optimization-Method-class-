"""Validate the archived first-passage records without rerunning simulations."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "lloyd_finite_sample"


def classify_hit(first_hit: int | None, stabilization_iteration: int) -> tuple[bool, bool]:
    terminal_state = stabilization_iteration - 1
    strict_preterminal = first_hit is not None and first_hit < terminal_state
    at_terminal = first_hit is not None and first_hit == terminal_state
    return strict_preterminal, at_terminal


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    dataset_rows = read_csv(RESULTS / "escape_time_by_dataset.csv")
    summary_rows = read_csv(RESULTS / "escape_time_summary.csv")
    trajectory_rows = read_csv(RESULTS / "escape_time_trajectories.csv")

    assert len(dataset_rows) == 480, f"expected 480 dataset records, got {len(dataset_rows)}"
    assert len(summary_rows) == 12, f"expected 12 summary rows, got {len(summary_rows)}"
    assert trajectory_rows, "trajectory CSV is empty"

    groups: dict[tuple[float, int], list[dict[str, str]]] = defaultdict(list)
    for row in dataset_rows:
        key = (float(row["tau"]), int(row["sample_size"]))
        groups[key].append(row)
        raw_hit = row["first_hit_iteration"].strip()
        first_hit = int(float(raw_hit)) if raw_hit else None
        if raw_hit:
            assert float(raw_hit).is_integer(), row
        stabilization = int(row["stabilization_iteration"])
        expected_preterminal, expected_terminal = classify_hit(first_hit, stabilization)
        assert (row["hit_before_stabilization"] == "True") == expected_preterminal, row
        assert (row["hit_at_terminal_state"] == "True") == expected_terminal, row

    # Explicitly exercise the one-index offset: stabilization_iteration is the
    # repeat-detection assignment call; the terminal state has index s - 1.
    assert classify_hit(4, 6) == (True, False)
    assert classify_hit(5, 6) == (False, True)
    assert classify_hit(6, 6) == (False, False)
    assert classify_hit(None, 6) == (False, False)

    summary_by_key = {
        (float(row["tau"]), int(row["sample_size"])): row for row in summary_rows
    }
    assert set(groups) == set(summary_by_key), "dataset/summary parameter grids differ"

    total_strict = 0
    total_terminal = 0
    for key in sorted(groups):
        records = groups[key]
        assert len(records) == 40, f"{key}: expected 40 records, got {len(records)}"
        assert {int(row["replicate"]) for row in records} == set(range(40)), key
        strict = sum(row["hit_before_stabilization"] == "True" for row in records)
        terminal = sum(row["hit_at_terminal_state"] == "True" for row in records)
        summary = summary_by_key[key]
        assert strict == int(summary["hit_count"]), (key, strict, summary["hit_count"])
        assert terminal == int(summary["terminal_state_hit_count"]), (key, terminal)
        assert abs(strict / 40 - float(summary["hit_fraction"])) < 1e-12, key
        total_strict += strict
        total_terminal += terminal
        print(
            f"tau={key[0]:.1f}, n={key[1]}: strict={strict}/40, "
            f"terminal={terminal}/40, conditional_median="
            f"{summary['median_hit_iteration_given_hit'] or 'undefined'}"
        )

    assert sum(bool(row["median_hit_iteration_given_hit"].strip()) for row in summary_rows) == 9
    print(
        f"PASS: {len(dataset_rows)} dataset records, {len(trajectory_rows)} trajectory rows, "
        f"12 parameter groups, 9 observed conditional medians; "
        f"strict hits={total_strict}, terminal-only hits={total_terminal}."
    )
    print("No simulation or confidence-interval estimation was run by this checker.")


if __name__ == "__main__":
    main()
