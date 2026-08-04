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

Both runs use three transmitter height regimes: low at `h_tx <= 60 m`, middle
at `60 m < h_tx <= 100 m`, and high at `h_tx > 100 m`. Each of the nine
topology and height combinations has its own recalibrated NLoS coefficients.
The approved nearest-prototype ITU topology router is unchanged.

## Completed full-split results

Both runs were calibrated only on the 10,840 official training maps and
evaluated on the 2,590 official test maps.

| LoS model | Overall RMSE | LoS RMSE | NLoS RMSE |
|---|---:|---:|---:|
| Coherent two ray with refitted rho, phi, bias, and radial residual | 1.928912 dB | 1.737044 dB | 3.536270 dB |
| FSPL with refitted radial residual only | 3.729323 dB | 3.744350 dB | 3.536270 dB |

The NLoS column is identical by design: the second run freezes the corrected
NLoS calibration from the first run so that the comparison isolates the LoS
model.

### Test RMSE by corrected ITU topology

| Topology | Maps | Two ray plus radial | FSPL plus refitted radial | Difference |
|---|---:|---:|---:|---:|
| Suburban | 1,455 | 1.697741 dB | 3.686547 dB | 1.988806 dB |
| Urban | 940 | 2.296267 dB | 3.772406 dB | 1.476139 dB |
| Dense urban | 195 | 2.571558 dB | 4.045490 dB | 1.473932 dB |

Changing from one mean roof height per connected footprint to one maximum
height per footprint increased gamma by 4.76% on average over nonempty test
maps. It changed 15 of 2,590 test assignments, all from suburban to urban.
The topology assignments remain the same as in the preceding corrected-router
run. The results above change because all nine NLoS coefficient sets were
refitted after replacing the earlier data-derived height cuts with 60 and
100 m.

## Rho/Phi ablation

This controlled test keeps the corrected ITU topology classification and its
NLoS calibration fixed. It changes only whether the LoS model includes the
coherent two-ray rho, phi, and bias terms. The radial correction is present
and recalibrated in both variants.

| Rho/Phi | Overall RMSE | LoS RMSE | NLoS RMSE |
|---|---:|---:|---:|
| With | 1.928912 dB | 1.737044 dB | 3.536270 dB |
| Without | 3.729323 dB | 3.744350 dB | 3.536270 dB |

The complete English table for global, suburban, urban, and dense urban
scopes is in
[`results/rho_phi_ablation/rho_phi_rmse.md`](results/rho_phi_ablation/rho_phi_rmse.md).

The corresponding model-with-rho/phi breakdown contains both the nine new
ITU-topology by antenna-bin groups and the three global antenna bins:
[`results/rho_phi_ablation/rho_phi_with_antenna_rmse.md`](results/rho_phi_ablation/rho_phi_with_antenna_rmse.md).

Updated replacements for the paper's main result table, physical-height
table, and surrounding numerical statements are in
[`results/rho_phi_ablation/paper_metric_replacements.md`](results/rho_phi_ablation/paper_metric_replacements.md).

## Commands

```powershell
python run_two_ray_itu3_building_max.py
python run_radial_only_itu3_building_max.py
python compare_corrected_runs.py
python evaluate_rho_phi_ablation.py
```
