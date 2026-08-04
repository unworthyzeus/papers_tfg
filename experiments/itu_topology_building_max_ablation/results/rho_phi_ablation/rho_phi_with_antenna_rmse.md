# RMSE by new ITU topology and antenna-height bin

All values use the coherent two-ray model with rho, phi, bias, and the
recalibrated radial correction. RMSE is pixel-weighted over the official
2,590-map test split, with building pixels excluded.

## New ITU topology x antenna bin (9 groups)

| Topology | Antenna bin | Height rule | Maps | Overall RMSE | LoS RMSE | NLoS RMSE |
|---|---|---|---:|---:|---:|---:|
| Suburban | Low | hTx <= 60 m | 509 | 1.879726 | 1.681307 | 3.325184 |
| Suburban | Mid | 60 m < hTx <= 100 m | 415 | 1.690112 | 1.625701 | 3.018839 |
| Suburban | High | hTx > 100 m | 531 | 1.537026 | 1.527675 | 2.242948 |
| Urban | Low | hTx <= 60 m | 319 | 2.619855 | 2.044186 | 4.022796 |
| Urban | Mid | 60 m < hTx <= 100 m | 297 | 2.353992 | 2.040472 | 3.560468 |
| Urban | High | hTx > 100 m | 324 | 2.007354 | 1.939455 | 2.817347 |
| Dense Urban | Low | hTx <= 60 m | 71 | 3.003371 | 2.284726 | 4.446786 |
| Dense Urban | Mid | 60 m < hTx <= 100 m | 61 | 2.733034 | 2.236759 | 4.138982 |
| Dense Urban | High | hTx > 100 m | 63 | 2.057376 | 1.916766 | 3.259358 |

## Global antenna bins (3 groups)

| Antenna bin | Height rule | Maps | Overall RMSE | LoS RMSE | NLoS RMSE |
|---|---|---:|---:|---:|---:|
| Low | hTx <= 60 m | 899 | 2.143673 | 1.792340 | 3.752598 |
| Mid | 60 m < hTx <= 100 m | 773 | 1.968180 | 1.774658 | 3.507952 |
| High | hTx > 100 m | 918 | 1.711741 | 1.669689 | 2.761975 |
