# Spectral Measurement Processing and Matrix Calibration

Measurement processing and concentration calibration for studying Na, Ca, K, and Mg interference in plasma emission spectra. This repository provides the available analysis tools associated with the mixture-of-experts research: detector-record parsing, background subtraction, replicate aggregation, matrix-specific calibration, and summaries of archived numerical results.

## Available workflows

| Entry point | Purpose |
| --- | --- |
| `scripts/process_spectrometer_records.py` | Convert detector records into background-corrected measurements and replicate summaries |
| `scripts/calibrate_matrix_condition.py` | Fit Cu, Ni, or Zn calibration within a selected Na/Ca/K/Mg condition |
| `scripts/summarize_archived_results.py` | Summarize historical model-error tables |
| `scripts/check_analysis.py` | Check parsing, aggregation, calibration, and invalid-input handling |
| `analysis/archived_results/` | Original numerical outputs grouped by analysis |
| `data/examples/` | Measured-spectrum table for inspecting the data format |

## Setup

Use Python 3.10–3.12 in a virtual environment.

```bash
python -m venv .venv
# Activate the environment before continuing.
python -m pip install -r requirements.txt
python scripts/check_analysis.py
python scripts/summarize_archived_results.py
```

No TensorFlow installation is required for these analysis workflows.

## Process detector records

```bash
python scripts/process_spectrometer_records.py measurements --output results/measurement-run
```

The input contains chronologically sorted groups of **one background record followed by ten signal records**, with 1,948 tab-separated wavelength/intensity rows per file. Acquisition conditions are encoded in the filenames. The processor checks file groups and wavelength consistency, subtracts the background, and writes `Concat.csv`, `Mean.csv`, `STD.csv`, `RSD.csv`, and `Mean_3.csv` to a new output folder.

Replicate summaries use sample standard deviations. `Mean_3.csv` averages complete consecutive groups of three within each condition, leaving a final one or two observations out of that specific summary. Zero-mean relative standard deviations are undefined and exported as empty values. Input files are never overwritten.

## Fit a matrix-specific calibration

```bash
python scripts/calibrate_matrix_condition.py data/examples/sodium_matrix_calibration.csv --metal Cu --matrix 0 0 0 0 --output results/calibration-run
```

The four matrix values specify Na, Ca, K, and Mg. Select a condition actually present in the input table. The command exports the slope, intercept, and training R² to `calibration.json`. Add `--testing-csv` to export predictions. For testing concentrations already expressed in ppm, set `--test-concentration-divisor 1`; the default of 10 retains the original experiment convention.

Optional reference-line and area normalization are exposed through `--normalization`. The historical area option uses different training and testing integration rules. See [reproduction notes](docs/REPRODUCIBILITY.md) before using it with new measurements.

## Research context and archived results

The original research investigated staged ion-specific experts and interference interactions. The shared `spice_moe.py` model implementation is absent from the supplied source archive. Model-training notebooks that depend on it are preserved privately, rather than supplied as executable entry points here. This repository does **not** currently provide a runnable mixture-of-experts model.

The included result tables are historical outputs. The summary command reports MAE, bias, and RMSE computed from their rounded error columns; it does not retrain or evaluate a recovered model. [Method notes](docs/METHOD.md), [analysis notes](analysis/README.md), and [data documentation](docs/DATA.md) explain their provenance and limits.

## Validation and data use

The analysis checks exercise raw-record parsing, known replicate means and sample standard deviations, calibration recovery, invalid input rejection, and preservation of input files. They do not establish a new scientific benchmark. Full research datasets and checkpoints remain in the source archive, with checksums in `data/external_artifacts.json`.

Original source and numerical data are preserved. No software or dataset license is included. Contact the repository owner regarding reuse or additional research materials.
