# RMSE by new ITU topology and antenna-height bin

All values use the coherent two-ray model with rho, phi, bias, and the
recalibrated radial correction. RMSE is pixel-weighted over the official
2,590-map test split, with building pixels excluded.

## New ITU topology x antenna bin (9 groups)

| Topology | Antenna bin | Height rule | Maps | Overall RMSE | LoS RMSE | NLoS RMSE |
|---|---|---|---:|---:|---:|---:|
| Suburban | Low | hTx <= 58.12 m | 484 | 1.883782 | 1.678704 | 3.345009 |
| Suburban | Mid | 58.12 m < hTx <= 103.85 m | 468 | 1.699505 | 1.636261 | 2.972276 |
| Suburban | High | hTx > 103.85 m | 503 | 1.524811 | 1.517532 | 2.155021 |
| Urban | Low | hTx <= 58.12 m | 301 | 2.644874 | 2.050202 | 4.045260 |
| Urban | Mid | 58.12 m < hTx <= 103.85 m | 335 | 2.347036 | 2.040480 | 3.554021 |
| Urban | High | hTx > 103.85 m | 304 | 1.987608 | 1.930839 | 2.720682 |
| Dense Urban | Low | hTx <= 58.12 m | 61 | 2.967731 | 2.276018 | 4.364450 |
| Dense Urban | Mid | 58.12 m < hTx <= 103.85 m | 75 | 2.792588 | 2.246364 | 4.259618 |
| Dense Urban | High | hTx > 103.85 m | 59 | 2.005211 | 1.899602 | 3.043231 |

## Global antenna bins (3 groups)

| Antenna bin | Height rule | Maps | Overall RMSE | LoS RMSE | NLoS RMSE |
|---|---|---:|---:|---:|---:|
| Low | hTx <= 58.12 m | 846 | 2.142552 | 1.787203 | 3.751065 |
| Mid | 58.12 m < hTx <= 103.85 m | 878 | 1.981378 | 1.784877 | 3.522459 |
| High | hTx > 103.85 m | 866 | 1.694075 | 1.659540 | 2.650380 |
