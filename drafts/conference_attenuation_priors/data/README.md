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
