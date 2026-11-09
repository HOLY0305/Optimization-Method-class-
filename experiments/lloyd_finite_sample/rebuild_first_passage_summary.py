"""Reclassify saved first-passage runs and rebuild their derived summaries."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from escape_time_study import SEED, summarize


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "lloyd_finite_sample"


def main() -> None:
    dataset_path = RESULTS / "escape_time_by_dataset.csv"
    datasets = pd.read_csv(dataset_path)

    # The stored counter is the assignment call that detects a repeated
    # partition; the returned terminal state has the preceding update index.
    first_hit = datasets["first_hit_iteration"]
    terminal_state = datasets["stabilization_iteration"] - 1
    datasets["hit_before_stabilization"] = first_hit.notna() & (first_hit < terminal_state)
    datasets["hit_at_terminal_state"] = first_hit.notna() & (first_hit == terminal_state)
    datasets.to_csv(dataset_path, index=False)

    summary_rng = np.random.default_rng(SEED + 1)
    summary = pd.DataFrame(
        [
            summarize(group, summary_rng)
            for _, group in datasets.groupby(["tau", "sample_size"], sort=True)
        ]
    )
    summary.to_csv(RESULTS / "escape_time_summary.csv", index=False)

    metadata_path = RESULTS / "escape_time_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["protocol"]["event"] = (
        "absolute normalized (1,-2,1)/sqrt(6) high-mode amplitude first reaches 0.4 "
        "strictly before the returned terminal fixed-point state; the repeat-detection "
        "assignment call is one index later than that state"
    )
    metadata["classification_rebuild"] = (
        "Strict preterminal hits and threshold hits exactly at the returned terminal "
        "state were classified from saved dataset-level first-hit and repeat-detection "
        "indices; raw trajectories were unchanged."
    )
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(summary.to_string(index=False, float_format=lambda value: f"{value:.3f}"))


if __name__ == "__main__":
    main()
