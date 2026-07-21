# Official split analysis artifacts

The `official_split_analysis/` directory contains the frozen nine-regime
COST231 NLoS calibration, validation component ablation, official test metrics,
per-city and height breakdowns, city bootstrap intervals, ground-only
visibility accounting, exact NLoS coefficients, applied-term diagnostics, the
configured-ray-tracer repeat audit, and same-machine CPU runtime measurements
used by the conference paper.

Regenerate the artifacts from the repository root with:

```powershell
python scripts\run_conference_attenuation_ablation.py
python scripts\analyze_nlos_terms.py
```

The script reads the original HDF5 data without modifying it and uses the
official Try 74/75 compatible city split. The large dataset is not duplicated
in this paper repository.

## Extended NLoS simplification study

The `official_split_analysis/extended_nlos_ablations/` directory contains a
separate research audit that is not used by the paper. It compares 28 NLoS
models, including nested reductions to one spatial scale, four, three, and two
features, calibrated COST231 and distance controls, and constant predictors.
Every variant is recalibrated on the 37 training cities before evaluation on
the unchanged validation and test city splits. Building pixels are excluded.

Regenerate this study from the repository root with:

```powershell
python scripts\run_extended_nlos_ablations.py
```
