# Reproducibility status and retained limitations

## Missing source

The canonical version-6 notebooks all import `spice_moe.py`. That module was absent from the supplied source tree and additional local filename/content searches. The original analysis documentation also references absent `matrix_calibration.py`, `calibration_per_matrix.py`, and additional analysis notebooks.

Model architecture, loss computation, sampling, splitting, checkpoint reconstruction, and most evaluation functions are delegated to the missing shared module. Syntax checks cannot establish runtime correctness without it. The notebooks now fail with a clear missing-runtime message before creating run artifacts. No substitute implementation was created.

## Historical evidence

The archive contains an executed notebook set dated 2026-09-08, stage checkpoint files, and analysis CSVs. An earlier HTML note states that TensorFlow training had not yet run; that statement predates the available executed notebook evidence and is not used as the current status.

The archived stage-1 output contains a severe Cu readout anomaly, while later-stage logs show different behavior. The snapshot is retained as research history, not presented as a fully resolved or uniformly successful experiment. Recovery of the exact source and environment is needed to investigate checkpoint lineage, numerical stability, and evaluation discrepancies.

## Evaluation limits

- Archived testing uses metal concentrations of 3 and 5 ppm. Two levels provide limited evidence for calibration shape or broader-range behavior.
- The final notebook fits calibration on clean rows from the test table and uses measurement repeatability estimated from testing. This is not an untouched external calibration-and-test protocol.
- `model_err` compares predicted and measured spectra after applying the same calibration curve. It differs from error against nominal metal concentration.
- The documented held-out-combination split must be verified in the recovered `split_plan` and stochastic sampler implementation. Augmented samples share measured replicate pools.
- A readout standard-deviation ratio near one is not sufficient to establish unbiased predictions or a correct calibration slope.
- Teacher regularization, replay of earlier conditions, and freezing older experts aim to reduce forgetting. They are not an independently demonstrated invariance guarantee.
- Several archived outputs are rounded; their values should not be represented as high-precision independent measurements.

## Standalone script assumptions

The interactive calibration script retains a division by 10 when reading nominal test concentrations. It also uses a different area-integration treatment for training and testing in its area-normalization option. Both behaviors come from the source and require experimental justification before reuse with new data. They were not silently changed during organization.

The raw-file processor assumes one background plus ten signal files per group and a specific wavelength grid for baseline subtraction. Its summary calculations preserve the original missing/incomplete-group handling and standard-deviation conventions.

## Curation changes

- Renamed the two standalone scripts and grouped latest notebooks, analysis tables, and documentation.
- Translated remaining non-English narrative, prompts, and docstrings. Rephrased unsupported guarantees in comments as methodological intentions.
- Cleared copied notebook outputs and incidental metadata; the original executed files remain in the private archive.
- Replaced personal absolute paths with configurable inputs and isolated run directories.
- Redirected CSV exports from the raw-file processor to a fresh output directory so selected inputs are not overwritten.
- Added entry-point guards and lightweight inspection utilities. Numerical model calls, hyperparameters, raw arrays, and experimental calculations were preserved.

## Checks performed

Every original file was copied and verified with SHA-256. Curated Python files and notebook code cells were compiled without running training. Notebook structure, empty outputs, English-only text/path names, personal-path removal, numerical literal preservation, and archived CSV integrity were checked. The archived-result summary was executed on the supplied tables using standard-library arithmetic.

These checks establish a clean, traceable source package. They do not reproduce the neural model or certify the scientific conclusions.
