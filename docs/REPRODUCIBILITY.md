# Reproducibility status and retained limitations

## Missing source

The canonical version-6 notebooks all import `spice_moe.py`. The matching module is not available in this repository or its research archive. The original analysis documentation also references absent `matrix_calibration.py`, `calibration_per_matrix.py`, and additional analysis notebooks.

Model architecture, loss computation, sampling, splitting, checkpoint reconstruction, and most evaluation functions are delegated to the missing shared module. Syntax checks cannot establish runtime correctness without it. The notebooks now fail with a clear missing-runtime message before creating run artifacts.

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

The interactive calibration script retains a division by 10 when reading nominal test concentrations. It also uses a different area-integration treatment for training and testing in its area-normalization option. Both behaviors come from the source and require experimental justification before reuse with new data. Check these conventions before applying the script to a different measurement protocol.

The raw-file processor assumes one background plus ten signal files per group and a specific wavelength grid for baseline subtraction. Its summary calculations preserve the original missing/incomplete-group handling and standard-deviation conventions.

## Implementation and validation

Paths are configurable, and runs write to isolated output directories. The raw-file processor leaves selected input files unchanged. Standalone analysis scripts use entry-point guards, so importing them does not start file dialogs or processing.

Validation covers Python syntax, notebook structure, numerical-table integrity, and execution of the archived-result summary. Readiness checks report the absent model module before notebook execution. Full neural training and inference remain unavailable without that dependency.
