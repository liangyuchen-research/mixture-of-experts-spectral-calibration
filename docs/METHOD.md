# Method and visible implementation

## Modeling direction

This project models the forward interference process:

```text
clean spectrum + metal/interferent conditions
    -> ion experts + router + saturation gate
    -> predicted spectral residual
    -> clean spectrum + residual
    -> predicted interfered spectrum
```

This direction matters: the model is not presented here as a denoiser that directly maps an unknown interfered spectrum back to a clean one. The associated calibration analyses investigate how predicted or measured matrix-dependent responses affect concentration estimates.

The diagram describes the original version-6 technical note and notebook call sites. Layer-level architecture, gating equations, and loss implementation reside in the missing `spice_moe.py`, so those details cannot be verified from this snapshot.

## Sampling

The preprocessing notebook builds raw spectral banks and row-index plans instead of materializing every possible augmented spectrum. For a requested Cu/Ni/Zn combination, it selects a background replicate and overwrites the corresponding metal windows with replicates at the requested concentrations. Interfered spectrum components remain within the same Na/Ca/K/Mg condition. A shared clean pool supplies missing clean concentration levels when needed.

Multiple-interferent conditions receive additional sampling weight. The archived preprocessing run reports 1,533,600 explicit index records across seven plans and 310 test pairs with 1,948 spectral values each. These index records are constructed samples, not independent experimental measurements. Claims about the full dynamic sampling space depend on the absent sampler implementation.

## Incremental stages

The visible stage notebooks pass `train_ions=["K"]` or `["Mg"]` when adding an expert and construct an earlier-stage teacher with `trainable=False`. The teacher is used on conditions where the new ion is absent. Earlier datasets are included in later stages. These calls document the intended freezing, rehearsal, and teacher-consistency scheme.

Shared routing and saturation components remain trainable according to the technical note. Freezing earlier expert weights alone does not prove that all earlier predictions remain exactly unchanged.

## Calibration-aware objectives

The technical note describes absolute and relative full-spectrum terms, metal-window terms, selected readout-wavelength terms, background distribution matching, and readout bias/gain/consistency terms. Repeatability-based tolerances are described for individual readout errors. The notebooks log these categories, but the missing module prevents checking their exact formulas and effective weights.

The final evaluation notebook visibly fits a linear readout-versus-concentration relationship on clean rows in the testing table, then applies the same relationship to predicted and measured interfered spectra. Its `model_err` columns are therefore differences between two calibration readouts. They are not identical to error against the nominal concentration.

## Validation

The notebook call sites use `S.split_plan(P)`. The original technical note describes holding out complete Cu/Ni/Zn combinations, and the archived evaluation log reports 22 held-out combinations out of 216. The split and training sampler cannot be independently audited until the missing module is recovered.

Shared raw replicate pools and constructed spectra affect sample independence. Calibration fitting and configured repeatability thresholds also use test information in the source workflow. These choices must be accounted for before interpreting results as an untouched external evaluation.
