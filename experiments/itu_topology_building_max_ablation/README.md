# ITU 3 building-maximum gamma ablation

This isolated experiment corrects the raster interpretation used to estimate
the ITU-R P.1410 gamma parameter.

P.1410-6 defines:

- alpha as the building-covered land fraction;
- beta as the mean number of buildings per square kilometre;
- gamma as the most probable, or mode, building height of a Rayleigh
  building-height distribution.

The recommendation works with buildings and a distribution of rooftop
heights. It does not prescribe whether an irregular raster footprint must be
reduced with a mean or a maximum. This experiment uses one observation per
four-connected footprint, equal to the maximum raster height in that
footprint, and estimates the Rayleigh mode with
`sqrt(mean(building_height^2) / 2)`. It does not give separate weight to every
building pixel.

The parameter definitions are in
[ITU-R P.1410-6](https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.1410-6-202308-I%21%21PDF-E.pdf),
Section 2.1.4, printed page 10 (PDF page 12). The exact four standard
environment tuples used by the classifier are reproduced in Table 2 of
[Saboor et al.](https://imec-publications.be/bitstreams/0b904d1a-eaf3-4112-aecb-6eda2b35a2d9/download),
printed page 367 (PDF page 4). See [`ITU_SOURCE.md`](ITU_SOURCE.md) for the
source distinction.

The known limitation is that touching raster footprints can be merged into a
single connected component.

Two complete runs use the unchanged official Try 74/75 compatible city
holdout:

1. LoS `FSPL + coherent two ray(rho, phi, bias) + radial residual`, with all
   LoS and NLoS calibrations refitted from training cities.
2. LoS `FSPL + r(d2D, hTx)`, with `r` refitted from FSPL and no rho, phi, or
   two-ray bias. The recalibrated NLoS coefficients from run 1 are frozen so
   only LoS changes.

All outputs remain below this directory. Earlier experiments, official code,
paper artifacts, and the HDF5 are not modified.

## Completed full-split results

Both runs were calibrated only on the 10,840 official training maps and
evaluated on the 2,590 official test maps.

| LoS model | Overall RMSE | LoS RMSE | NLoS RMSE |
|---|---:|---:|---:|
| Coherent two ray with refitted rho, phi, bias, and radial residual | 1.928750 dB | 1.737044 dB | 3.535074 dB |
| FSPL with refitted radial residual only | 3.729239 dB | 3.744350 dB | 3.535074 dB |

The NLoS column is identical by design: the second run freezes the corrected
NLoS calibration from the first run so that the comparison isolates the LoS
model.

### Test RMSE by corrected ITU topology

| Topology | Maps | Two ray plus radial | FSPL plus refitted radial | Difference |
|---|---:|---:|---:|---:|
| Suburban | 1,455 | 1.697705 dB | 3.686530 dB | 1.988826 dB |
| Urban | 940 | 2.296086 dB | 3.772296 dB | 1.476210 dB |
| Dense urban | 195 | 2.570365 dB | 4.044732 dB | 1.474367 dB |

Changing from one mean roof height per connected footprint to one maximum
height per footprint increased gamma by 4.76% on average over nonempty test
maps. It changed 15 of 2,590 test assignments, all from suburban to urban.
The corrected two-ray overall RMSE differs from the earlier mean-height run by
only +0.000002 dB, so the numerical conclusion is unchanged even though the
raster interpretation is now clearer.

## Rho/Phi ablation

This controlled test keeps the corrected ITU topology classification and its
NLoS calibration fixed. It changes only whether the LoS model includes the
coherent two-ray rho, phi, and bias terms. The radial correction is present
and recalibrated in both variants.

| Rho/Phi | Overall RMSE | LoS RMSE | NLoS RMSE |
|---|---:|---:|---:|
| With | 1.928750 dB | 1.737044 dB | 3.535074 dB |
| Without | 3.729239 dB | 3.744350 dB | 3.535074 dB |

The complete English table for global, suburban, urban, and dense urban
scopes is in
[`results/rho_phi_ablation/rho_phi_rmse.md`](results/rho_phi_ablation/rho_phi_rmse.md).

## Commands

```powershell
python run_two_ray_itu3_building_max.py
python run_radial_only_itu3_building_max.py
python compare_corrected_runs.py
python evaluate_rho_phi_ablation.py
```
