# Data schema and artifact layout

## Measurement tables

The inspected sodium-matrix `Concat.csv` has 300 records and includes an exported row index, timestamp, acquisition metadata, sample concentrations, 1,948 wavelength intensities, and derived calibration columns. Numeric wavelength headers cover approximately 199.820-530.110 nm.

The model-facing metadata order is:

```text
Voltage, Ontime, Offtime, Cycle, Conductivity,
Cu, Ni, Zn, Na, Ca, K, Mg
```

The raw record parser reads groups of 11 TXT files: one background record followed by ten signal records. It subtracts the background and decodes conditions from the filename. The `Conc` filename field is assigned to Cu, Ni, and Zn, so the raw acquired metal levels are diagonal before augmentation. The parser assumes ordered files and a matching 1,948-point instrument grid.

`Mean.csv` summarizes available replicates by condition. `Mean_3.csv` averages consecutive groups of three observations and omits the incomplete remainder from the derived table. This omission is part of the original aggregation algorithm; source records remain intact. `data/examples/sodium_matrix_mean_spectra.csv` preserves the header and first six rows of the sodium-matrix `Mean_3.csv`. The complete `sodium_matrix_calibration.csv` table is copied byte-for-byte from the original sodium-matrix `Mean.csv` and supports the documented calibration command.

Acquisition-field units are not inferred where the supplied files do not establish them. Metal/interferent concentrations are labeled in ppm by the original calibration workflow.

## Prepared data

The test HDF5 pair contains `X_with_meta`/`X_columns` and `Y_with_meta`/`Y_columns`. The inspected CSV counterpart has 310 rows and 1,960 columns: 12 metadata values plus 1,948 spectral intensities.

Training-plan HDF5 files store:

| Key | Meaning in the preprocessing code |
| --- | --- |
| `meta` | Explicit sampled condition rows |
| `x_idx`, `y_idx` | Replicate indices used to assemble clean/interfered spectra |
| `x_bank`, `y_bank` | Raw clean and interfered spectral banks |
| `g_meta`, `g_lv`, `g_bg`, `g_w` | Group conditions, level/background ranges, and sampling weights |
| `x_lv` | Clean-bank row ranges by concentration level |
| `wl`, `columns` | Wavelength grid and metadata/spectrum column labels |

Metal-window ranges are stored as HDF5 attributes. Normalization and model metadata constants must come from the matching shared module; replacing them from another project would change the experiment.

## External-artifact manifest

`external_artifacts.json` records archive-relative paths, destination paths, byte counts, and SHA-256 hashes for 59 input/checkpoint artifacts. Relative measurement folder names are retained to match the original notebook mappings. The restore script copies them into a new local directory without overwriting conflicting files.

The remainder of the verified private archive includes raw TXT records, older code variants, complete notebook execution histories, generated spectra, figures, and presentation slides. None were deleted. Slides and figures were not added to the candidate repository because their visible language and metadata were not reviewed for publication.
