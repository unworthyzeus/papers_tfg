# Paper metric replacements after the corrected ITU recalibration

These values use the coherent two-ray model with rho, phi, bias, and the
recalibrated radial correction. The NLoS branch uses the new three-class ITU
routing with one maximum height observation per connected building footprint.
Calibration uses only the 10,840 official training maps. Evaluation uses the
2,590 maps from the 14 official held-out test cities.

## Replacement for Table V

| Metric | Estimate | 95% interval |
|---|---:|---:|
| Overall RMSE [dB] | 1.9287 | [1.7984, 2.0956] |
| Overall MAE [dB] | 1.2170 | [1.1371, 1.3177] |
| LoS RMSE [dB] | 1.7370 | [1.6603, 1.8225] |
| NLoS RMSE [dB] | 3.5351 | [3.2340, 3.8457] |
| Macro city RMSE [dB] | 1.9829 | [1.8494, 2.1292] |

Replacement results text:

> Table V gives the final attenuation-only test result. The prior reaches
> 1.9287 dB RMSE and 1.2170 dB MAE across all valid receiver pixels. The LoS
> error is 1.7370 dB. NLoS remains the hard regime at 3.5351 dB, consistent
> with the unobserved identity of the dominant diffracted or reflected path
> after direct-path blockage.

Replacement city text:

> Per-city RMSE ranges from 1.6149 dB in Halifax to 2.5832 dB in Osaka; the
> unweighted 14-city mean is 1.9829 dB. This spread and the city-bootstrap
> interval prevent the global score from being read as uniform performance
> across environments.

## Replacement for Table VII

| Height | Overall RMSE | LoS RMSE | NLoS RMSE | Maps |
|---|---:|---:|---:|---:|
| 12--50 m | 2.1932 | 1.7943 | 3.8367 | 624 |
| 50--150 m | 1.9533 | 1.7788 | 3.4217 | 1,385 |
| 150--300 m | 1.6556 | 1.6370 | 2.3540 | 387 |
| 300--500 m | 1.5591 | 1.5496 | 2.2816 | 194 |

Replacement height text:

> Table VII shows the frozen prior on the final test cities only for four
> physical height intervals. Error decreases from 2.1932 dB at 12--50 m to
> 1.5591 dB above 300 m.

## Other repeated paper numbers

Abstract and conclusion: replace overall RMSE `1.9277` with `1.9287` and NLoS
RMSE `3.5275` with `3.5351`. LoS RMSE remains `1.7370`.
