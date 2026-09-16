# Reproduction notes

## Public analysis workflow

The command-line entry points require NumPy, pandas, and scikit-learn. Paths are supplied as arguments. Outputs are written to new directories, and a pre-existing destination is rejected. The raw-record parser validates complete groups, finite values, and consistent wavelength grids before writing results.

The maintained implementation retains the original detector count, filename conditions, background subtraction, wavelength-specific baselines, sample standard deviations, and consecutive groups of three. Grouping uses only observed condition combinations instead of iterating through a Cartesian product. Invalid or incomplete record groups now fail explicitly instead of silently dropping measurements. The raw input is never modified.

The calibration retains the original peak/background wavelengths and nearest-grid selection. Zero/nonfinite normalization references and noninvertible calibration slopes now raise a descriptive error. The original testing-label division by 10 is an explicit argument. Its historical area-normalization option still masks specified windows during training and integrates the first 400 positions during testing. This asymmetry requires experimental justification before reuse.

## Preserved model research

The original version-6 notebooks import an unavailable `spice_moe.py` module. Architecture, losses, sampling, data splitting, checkpoint construction, and most model evaluation are delegated to that missing source. Earlier analysis notes also refer to unavailable `matrix_calibration.py` and `calibration_per_matrix.py` files.

These dependent notebook copies are preserved in the private research archive with hashes. They are not runnable public entry points. No replacement model was invented from descriptive notes or checkpoints. The available measurement-processing, calibration, and archived-result code is independent of that runtime.

## Interpretation of archived outputs

- Testing tables include only 3 and 5 ppm metal concentrations, which limits calibration-range conclusions.
- Historical evaluation fits calibration using clean rows in the testing table and estimates repeatability from testing. It is not an untouched external calibration/test protocol.
- `model_err` compares predicted and measured spectral readouts under the same calibration, rather than errors against nominal concentration.
- The model source is needed to verify split logic and checkpoint lineage. Augmented examples may share measured replicate pools.
- Rounded numerical tables support descriptive summaries, not high-precision independent performance claims.
- An archived stage-1 Cu readout anomaly remains unresolved. No new model results are claimed.

## Validation scope

`python scripts/check_analysis.py` tests synthetic acquisition groups and exact analytical cases, including rejected incomplete groups, invalid references, and zero calibration slopes. `summarize_archived_results.py` is run against all four included stage tables. Syntax and numerical-table hashes are checked separately. Neural training and inference cannot be reproduced without the original model source.
