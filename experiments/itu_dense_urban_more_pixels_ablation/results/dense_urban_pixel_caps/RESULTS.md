# Dense Urban NLoS pixel-cap ablation

Only the three Dense Urban NLoS ridge regimes were recalibrated. LoS,
Suburban, and Urban stayed frozen. All fitting used the official 10,840-map
training split; candidate selection used Dense Urban validation maps only.
The test split was evaluated once with the selected cap.

The validation-selected cap is **4,096 NLoS pixels per Dense Urban map**.
The 1,024-pixel refit reproduces the frozen coefficients with maximum absolute difference 0.000e+00.

## Dense Urban validation selection

| Pixel cap | Maps | Overall RMSE | LoS RMSE | NLoS RMSE |
|---:|---:|---:|---:|---:|
| 1,024 | 255 | 2.363625 | 2.041881 | 3.530755 |
| 2,048 | 255 | 2.363597 | 2.041881 | 3.530646 |
| 4,096 | 255 | 2.363329 | 2.041881 | 3.529594 |
| 8,192 | 255 | 2.363743 | 2.041881 | 3.531218 |

## Official Dense Urban test result

| Variant | Maps | Overall RMSE | LoS RMSE | NLoS RMSE |
|---|---:|---:|---:|---:|
| baseline_cap_1024 | 195 | 2.570365 | 2.112632 | 4.127528 |
| selected_cap_4096 | 195 | 2.569633 | 2.112632 | 4.124852 |

## Global test metric after replacing only Dense Urban

| Maps | Overall RMSE | LoS RMSE | NLoS RMSE |
|---:|---:|---:|---:|
| 2,590 | 1.928699 | 1.737044 | 3.534700 |

## Interpretation

The selected cap changes Dense Urban test NLoS RMSE by -0.002676 dB
and global NLoS RMSE by -0.000375 dB. Global MAE changes by
+0.000010 dB. This is not a material improvement, so the frozen
1,024-pixel calibration remains the paper result.
