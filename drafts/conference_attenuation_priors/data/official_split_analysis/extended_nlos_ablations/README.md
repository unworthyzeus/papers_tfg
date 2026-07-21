# Extended NLoS simplification audit

This directory is a research artifact and is not consumed by the conference
paper. It extends the official Try 78 component study with nested reductions
of the NLoS linear model.

## Evaluation contract

- Try 74/75 compatible city holdout with split seed 42.
- Calibration uses 10,840 maps from 37 training cities only.
- Validation uses 2,750 maps and final test uses 2,590 maps.
- Building pixels and invalid ground targets are excluded.
- Each feature subset is standardized and fitted independently with ridge
  regularization. Ablation does not mean zeroing frozen coefficients.
- The LoS model is unchanged while NLoS variants are compared.

## Main test results

| NLoS model | NLoS RMSE (dB) | Overall RMSE (dB) | Overall increase (dB) |
|---|---:|---:|---:|
| Full 14-feature, nine-regime model | 3.5275 | 1.9277 | 0.0000 |
| Only 41-pixel morphology plus geometry, 8 features | 3.5497 | 1.9307 | 0.0030 |
| `log1p_d2d`, `density_41`, `nlos_41`, bias, nine regimes | 3.5713 | 1.9337 | 0.0060 |
| Same four features, topology routing only | 3.5758 | 1.9343 | 0.0066 |
| `log1p_d2d`, `density_41`, bias, topology routing only | 3.5947 | 1.9369 | 0.0092 |
| Distance and bias only, nine regimes | 3.7159 | 1.9538 | 0.0261 |
| Calibrated COST231 and bias only, nine regimes | 3.7253 | 1.9551 | 0.0274 |
| One global NLoS constant | 4.5403 | 2.0789 | 0.1512 |

All 15 additional reductions worsen both validation and test metrics. The
41-pixel scale is more informative than the 15-pixel scale: removing the
15-pixel features raises test NLoS RMSE by 0.0066 dB, whereas removing the
41-pixel family raises it by 0.0948 dB.

## Interpretation

The small conditional NLoS degradation does not imply that city morphology is
irrelevant to propagation. The visibility mask is supplied to the predictor,
so the experiment does not ask the regression to discover whether a receiver
is obstructed. Morphology can strongly control the spatial support of NLoS
while having a smaller effect on the attenuation value after the receiver is
already known to be NLoS.

The remaining inputs are also redundant. Local NLoS fraction encodes the
visibility pattern, local density encodes buildings, and topology routing
encodes map-level morphology. Removing one family leaves other morphology
proxies available. Even the four-feature model is therefore not morphology
free.

Removing all local morphology and visibility together raises test NLoS RMSE
from 3.5275 to 3.6978 dB. Removing the spatial predictors down to a global
constant raises it to 4.5403 dB. Morphology and spatial structure matter, but
the full 14-feature parameterization contains substantially more redundancy
than the test error requires.

The pixel-weighted overall metric further compresses NLoS changes because
NLoS accounts for 7.413% of valid test receivers. NLoS RMSE should therefore
be used when judging these variants, with overall RMSE reported only as the
deployment aggregate.

## Files

- `component_ablation_metrics.csv`: validation and test metrics for every
  variant.
- `recalibrated_models.json`: exact feature subsets, coefficients, fit
  diagnostics, and calibration contract.
- `summary.json`: compact machine-readable run summary.
- `scripts/run_extended_nlos_ablations.py`: reproduction script at repository
  root level.
