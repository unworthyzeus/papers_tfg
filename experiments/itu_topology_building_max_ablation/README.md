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

Official source: [ITU-R P.1410-6](https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.1410-6-202308-I%21%21PDF-E.pdf).

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

## Rho/Phi and ITU factorial ablation

The controlled 2 x 2 test keeps a recalibrated radial correction in every
variant. It changes only the coherent two-ray rho/phi/bias terms and the NLoS
topology conditioning. Without ITU means one global NLoS ridge calibration.

| Rho/Phi | ITU topology | Overall RMSE | LoS RMSE | NLoS RMSE |
|---|---|---:|---:|---:|
| With | With | 1.928750 dB | 1.737044 dB | 3.535074 dB |
| With | Without | 1.931703 dB | 1.737044 dB | 3.556758 dB |
| Without | With | 3.729239 dB | 3.744350 dB | 3.535074 dB |
| Without | Without | 3.730767 dB | 3.744350 dB | 3.556758 dB |

The complete English table for global, suburban, urban, and dense urban
scopes is in
[`results/rho_phi_itu_factorial/factorial_rmse.md`](results/rho_phi_itu_factorial/factorial_rmse.md).

## Commands

```powershell
python run_two_ray_itu3_building_max.py
python run_radial_only_itu3_building_max.py
python compare_corrected_runs.py
python evaluate_rho_phi_itu_factorial.py
```
