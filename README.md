# Mixture-of-Experts Spectral Calibration

Research workflows for modeling Na, Ca, K, and Mg matrix interference in plasma emission spectra used for Cu, Ni, and Zn quantification. The version-6 design predicts an interfered spectrum from a clean reference and an interference condition, supporting analysis of matrix-dependent calibration behavior.

**Snapshot status:** the original shared module `spice_moe.py` is missing from the supplied files. This repository preserves the latest orchestration notebooks, standalone spectrometer/calibration scripts, and archived numerical results. Model training and inference require recovery of that exact module. No replacement model has been invented.

## Research approach

The documented architecture combines ion-specific experts, a shared router, and a saturation gate. Three stages introduce interferents progressively:

| Stage | Active experts | Training intent |
| --- | --- | --- |
| 1 | Na, Ca | Train the initial experts and shared interaction components |
| 2 | Na, Ca, K | Add K, freeze earlier experts, and use a stage-1 teacher with rehearsal |
| 3 | Na, Ca, K, Mg | Add Mg with a stage-2 teacher and earlier-condition rehearsal |

The saturation gate is intended to represent interactions that a purely additive sum of single-ion effects would miss. Calibration readouts depend on peak, background, and reference-wavelength intensities, so the documented objectives include both metal windows and spectral-background behavior. [Method notes](docs/METHOD.md) distinguish the visible workflow from details delegated to the missing module.

## Repository contents

| Path | Content |
| --- | --- |
| `notebooks/00_run_all.ipynb` | Central configuration and sequential notebook runner |
| `notebooks/01_data_preprocessing.ipynb` | Compact spectral replicate banks and sampling plans |
| `notebooks/02_stage1_naca.ipynb` | Na/Ca training stage |
| `notebooks/03_stage2_add_k.ipynb` | Incremental K stage |
| `notebooks/04_stage3_add_mg.ipynb` | Incremental Mg stage |
| `notebooks/05_testing_evaluation.ipynb` | Spectral evaluation and concentration readout export |
| `scripts/process_spectrometer_records.py` | Raw-file parsing, background subtraction, and replicate aggregation |
| `scripts/calibrate_matrix_condition.py` | Interactive matrix-specific linear calibration |
| `scripts/summarize_archived_results.py` | Standard-library summary of archived model-error tables |
| `analysis/archived_results/` | Unchanged historical CSV results, grouped by analysis type |
| `data/examples/` | A small measured-spectrum table for inspecting the format |
| `src/README.md` | Missing shared-runtime description |

## Inspect the archived results

The numerical summary utility runs with the Python standard library and does not load model weights:

```bash
python scripts/summarize_archived_results.py
```

It calculates MAE, signed bias, and RMSE from the **stored, rounded model-error columns**. These are summaries of historical outputs, not newly reproduced model results. The original measurements, complete executed notebooks, and model files are retained in a separate private archive.

## Environment and standalone scripts

Use a separate Python environment for the scientific dependencies:

```bash
python -m venv .venv
# Activate the environment for your shell.
python -m pip install -r requirements.txt
python scripts/check_readiness.py
```

The requirements were inferred from visible imports. They are not an exact research environment lockfile, and the missing module may require additional dependencies or a specific TensorFlow/Keras version. The readiness command reports missing dependencies without starting training.

The standalone scripts do not depend on `spice_moe.py`. They use Tk file dialogs and require a graphical desktop:

```bash
python scripts/process_spectrometer_records.py
python scripts/calibrate_matrix_condition.py
```

Select the intended measurement folder or CSV when prompted. The record-processing script writes derived tables to a fresh directory under `results/`; it does not overwrite the selected input files. Original numeric calculations and interactive choices are retained.

## Restore data and recover the model workflow

The complete private archive contains 3,071 files totaling approximately 570 MB. All original files were copied and verified using SHA-256 before curation. A manifest identifies 59 artifacts used by the latest workflow, including prepared datasets, raw summary tables, and stage checkpoints.

```bash
python scripts/restore_local_data.py --archive-root "/path/to/private/raw-archive"
```

The utility verifies hashes, copies the listed artifacts into `data/local/`, and refuses to replace files with different content. It does not modify the archive. The manifest is not a public download endpoint.

After recovering the matching `spice_moe.py` into `src/`, launch Jupyter from the repository root. The runner creates a separate experiment directory, copies prepared data/checkpoints into that directory, and shares it across stages. `MOE_DATA_DIR` selects another local input directory; `MOE_OUTPUT_DIR` selects the output root. The notebook runner creates a fresh run; individually executed stage notebooks share `MOE_RUN_DIR` within the session.

The preserved full training defaults are 1,200 epochs for stage 1 and 800 for stages 2 and 3, with early stopping. No training or inference was launched during repository preparation.

## Interpretation and provenance

See [data documentation](docs/DATA.md), [archived-result notes](analysis/README.md), and [reproducibility limits](docs/REPRODUCIBILITY.md). The snapshot contains historical experiments with unresolved behavior; it does not establish general accuracy, no-forgetting guarantees, or deployment readiness.

All curated filenames and narrative text are English. Original files, older code versions, slides, and unreviewed figures remain in the private archive. File mappings are recorded in [FILE_MAPPING.json](docs/FILE_MAPPING.json). No license was supplied, so none has been invented; contact the repository owner about reuse and access to complete data.
