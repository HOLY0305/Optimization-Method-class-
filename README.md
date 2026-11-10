# Fixed-Capacity Lloyd Course Reproduction

[English](README.md) | [简体中文](README.zh-CN.md)

This repository contains the code and saved synthetic results for Section 4 of the course paper **“Optimization Modeling and Local Stability of the Fixed-Capacity Lloyd Algorithm.”** It supports checking the archived dataset-level records and reproducing the paper's two experimental plots without rerunning the 480-dataset simulation.

## Environment

- Python 3.13.9 (the recorded run used this version)
- Install the pinned Python dependencies with:

```powershell
python -m pip install -r requirements.txt
```

The figure script uses a CJK font (`Microsoft YaHei` on the recorded Windows environment). On another system, install a compatible Chinese font or change the font setting in the plot script.

## Reproduce the saved results

Run these commands from the repository root:

```powershell
python checks/verify_saved_results.py
python scripts/plot_paper_figures.py
```

The first command checks all 480 dataset records, the strict-preterminal versus terminal-only event boundary, and the stored 12-group summary. It does not rerun Lloyd or recalculate confidence intervals. The second reads `escape_time_summary.csv` and writes `fig03_empirical_hit_fraction` and `fig04_conditional_hit_iterations` as PNG and SVG under `figures/lloyd_finite_sample/`.

## Repository layout

```text
checks/        Validate saved dataset records and summary results
docs/          Experiment protocol and data dictionary
experiments/   Lloyd simulation and shared implementation
figures/       Saved paper figures (PNG and SVG)
results/       Dataset, trajectory, summary, and metadata files
scripts/       Plot the paper figures from the saved summary CSV
```

## Optional full simulation

To regenerate the experiment data from the fixed seed, run:

```powershell
python experiments/lloyd_finite_sample/escape_time_study.py
```

This executes all 480 independent datasets and overwrites the CSV/metadata files under `results/lloyd_finite_sample/`. The archived run recorded about 597 seconds; runtime depends on hardware and software. The complete saved dataset, trajectory and summary CSVs occupy under 300 kB. After a full run, execute the two saved-result commands above to verify and redraw the paper figures.

## Protocol and data

The parameter grid, stopping and event counters, random seed, confidence intervals, data fields and paper mapping are documented in [`docs/PAPER_EXPERIMENT_PROTOCOL.md`](docs/PAPER_EXPERIMENT_PROTOCOL.md) and [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md). All data are synthetic Gaussian samples and derived algorithm trajectories; no personal data are included. The `0.4` threshold was informed by an earlier exploratory run, fixed before this follow-up, and not preregistered. It is descriptive and is not the theoretical `1/3` local-spectrum boundary.

## Scope and limitations

The default workflow verifies and plots the saved outputs. It does not claim an independent rerun of the full simulation or a finite-sample proof of the population local-stability result. The files in this repository are limited to the current course paper's Section 4; older exploratory studies and unrelated high-order research outputs are intentionally excluded.

Python source code is under the MIT License in [`LICENSE`](LICENSE). Synthetic data, figures and documentation are under [CC BY 4.0](DATA_LICENSE.md).
