# Paper metric replacements after the 60/100 m recalibration

These values use the coherent two-ray model with rho, phi, bias, and the
recalibrated radial correction. The NLoS branch uses the new three-class ITU
routing with one maximum height observation per connected building footprint.
Calibration uses only the 10,840 official training maps. Evaluation uses the
2,590 maps from the 14 official held-out test cities.

The approved topology router is unchanged. Transmitter heights are routed as
low at $h_{\mathrm{tx}}\leq60$ m, middle at
$60<h_{\mathrm{tx}}\leq100$ m, and high above 100 m. All nine topology and
height coefficient sets were recalibrated.

## Replacement for Table V

| Metric | Estimate | 95% interval |
|---|---:|---:|
| Overall RMSE [dB] | 1.9289 | [1.7985, 2.0960] |
| Overall MAE [dB] | 1.2170 | [1.1371, 1.3177] |
| LoS RMSE [dB] | 1.7370 | [1.6603, 1.8225] |
| NLoS RMSE [dB] | 3.5363 | [3.2335, 3.8482] |
| Macro city RMSE [dB] | 1.9831 | [1.8495, 2.1297] |

Replacement results text:

> Table V gives the final attenuation-only test result. The prior reaches
> 1.9289 dB RMSE and 1.2170 dB MAE across all valid receiver pixels. The LoS
> error is 1.7370 dB. NLoS remains the hard regime at 3.5363 dB, consistent
> with the unobserved identity of the dominant diffracted or reflected path
> after direct-path blockage.

Replacement city text:

> Per-city RMSE ranges from 1.6149 dB in Halifax to 2.5851 dB in Osaka; the
> unweighted 14-city mean is 1.9831 dB. This spread and the city bootstrap
> interval prevent the global score from being read as uniform performance
> across environments.

## Replacement for the fitted height table

| Height | Overall RMSE | LoS RMSE | NLoS RMSE | Maps |
|---|---:|---:|---:|---:|
| Low, $h_{\mathrm{tx}}\leq60$ m | 2.1437 | 1.7923 | 3.7526 | 899 |
| Middle, $60<h_{\mathrm{tx}}\leq100$ m | 1.9682 | 1.7747 | 3.5080 | 773 |
| High, $h_{\mathrm{tx}}>100$ m | 1.7117 | 1.6697 | 2.7620 | 918 |

Replacement height text:

> The table uses exactly the three fitted transmitter height regimes. Error
> decreases from 2.1437 dB in the low regime to 1.7117 dB in the high regime.

## Other repeated paper numbers

Abstract and conclusion: use overall RMSE `1.9289`, NLoS RMSE `3.5363`, and
LoS RMSE `1.7370`.
