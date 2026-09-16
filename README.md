# Mixture-of-Experts Spectral Calibration

Research on modeling Na, Ca, K, and Mg matrix interference in plasma emission spectra for Cu, Ni, and Zn quantification. The staged workflow predicts an interfered spectrum from a clean reference and an interference condition, then analyzes the resulting concentration calibration.

**Implementation status:** the shared model module, `spice_moe.py`, is not included. The notebooks document the staged experiments but require that module for training and inference. The standalone measurement-processing scripts and archived-result summary utility are available independently.

## Research approach

The design combines ion-specific experts, a shared router, and a saturation gate. Training introduces interferents in three stages:

| Stage | Active experts | Training approach |
| --- | --- | --- |
| 1 | Na, Ca | Train the initial experts and shared interaction components |
| 2 | Na, Ca, K | Add K with frozen earlier experts, a stage-1 teacher, and rehearsal |
| 3 | Na, Ca, K, Mg | Add Mg with a stage-2 teacher and earlier-condition rehearsal |

The saturation gate models interactions beyond additive single-ion effects. Calibration depends on peak, background, and reference-wavelength intensities, so the objectives consider both metal-emission windows and spectral-background behavior. [Method notes](docs/METHOD.md) describe the workflow and distinguish visible notebook operations from functions in the missing module.

## Repository guide

| Path | Content |
| --- | --- |
| `notebooks/00_run_all.ipynb` | Configuration and sequential notebook runner |
| `notebooks/01_data_preprocessing.ipynb` | Spectral replicate banks and sampling plans |
| `notebooks/02_stage1_naca.ipynb` | Initial Na/Ca training stage |
| `notebooks/03_stage2_add_k.ipynb` | Incremental potassium stage |
| `notebooks/04_stage3_add_mg.ipynb` | Incremental magnesium stage |
| `notebooks/05_testing_evaluation.ipynb` | Spectral evaluation and concentration readouts |
| `scripts/process_spectrometer_records.py` | Raw-file parsing, background subtraction, and replicate aggregation |
| `scripts/calibrate_matrix_condition.py` | Interactive matrix-specific linear calibration |
| `scripts/summarize_archived_results.py` | Summary of stored model-error tables |
| `analysis/archived_results/` | Historical numerical results grouped by analysis |
| `data/examples/` | Measured-spectrum table for format inspection |

## Inspect the numerical results

The summary utility uses only the Python standard library:

```bash
python scripts/summarize_archived_results.py
```

It calculates MAE, signed bias, and RMSE from stored, rounded error columns. These are summaries of historical outputs, not a new model evaluation. The [analysis notes](analysis/README.md) explain the table schemas and interpretation.

## Standalone measurement analysis

Create a separate Python environment and activate it with `.venv\Scripts\activate` on Windows or `source .venv/bin/activate` on macOS/Linux.

```bash
python -m venv .venv
# Activate the environment before continuing.
python -m pip install -r requirements-analysis.txt
python scripts/process_spectrometer_records.py
python scripts/calibrate_matrix_condition.py
```

These scripts use Tk file dialogs and require a graphical desktop. Select the measurement folder or CSV when prompted. Record processing writes derived tables to a fresh directory under `results/`, leaving input files unchanged. The [reproduction notes](docs/REPRODUCIBILITY.md) explain the expected record groups and calibration assumptions.

## Model workflow requirements

`requirements.txt` lists dependencies visible in the notebooks. The missing module may require a specific TensorFlow/Keras version or additional packages. Check availability without starting training:

```bash
python scripts/check_readiness.py
```

The command reports dependencies and exits with a nonzero status while the model runtime is unavailable. Recover the matching `spice_moe.py` into `src/` before attempting a model run.

The external-artifact manifest lists 59 prepared datasets, measurement tables, and stage checkpoints. If the matching research archive is available, restore them with:

```bash
python scripts/restore_local_data.py --archive-root "/path/to/research-archive"
```

The utility verifies checksums and copies inputs into `data/local/` without overwriting different content. The manifest is an inventory, not a download service. Start Jupyter from the repository root after restoring the runtime and inputs. `MOE_DATA_DIR` selects the input directory and `MOE_OUTPUT_DIR` selects the output root. The runner creates a fresh experiment directory and shares it across stages through `MOE_RUN_DIR`.

Training defaults are 1,200 epochs for stage 1 and 800 for stages 2 and 3, with early stopping. Full training and inference have not been reproduced from this repository.

## Interpretation and data use

Archived experiments include unresolved calibration behavior. In particular, model-error columns compare predicted and measured spectral readouts under a shared calibration, rather than measuring error against nominal concentration. See the [data documentation](docs/DATA.md) and [reproduction limits](docs/REPRODUCIBILITY.md) before interpreting results.

The [file mapping](docs/FILE_MAPPING.json) records source and repository paths. Original numerical tables and archived model files are retained. No software or dataset license is included; contact the repository owner regarding reuse or access to complete data.
