# Rho/Phi and ITU topology factorial ablation

All values are pixel-weighted RMSE in dB on the 2,590 official held-out test maps.
Buildings are excluded. Every variant includes a radial correction `r(d2D, hTx)`
recalibrated on the 10,840 official training maps.

`Without ITU` means one global NLoS ridge calibration. `With ITU` means
three topology-specific NLoS ridge calibrations with per-sample routing.

| Scope | Rho/Phi | ITU topology | Maps | Overall RMSE | LoS RMSE | NLoS RMSE |
|---|---|---|---:|---:|---:|---:|
| Global | With | With | 2,590 | 1.928750 | 1.737044 | 3.535074 |
| Global | With | Without | 2,590 | 1.931703 | 1.737044 | 3.556758 |
| Global | Without | With | 2,590 | 3.729239 | 3.744350 | 3.535074 |
| Global | Without | Without | 2,590 | 3.730767 | 3.744350 | 3.556758 |
| Suburban | With | With | 1,455 | 1.697705 | 1.604754 | 3.162750 |
| Suburban | With | Without | 1,455 | 1.699390 | 1.604754 | 3.184575 |
| Suburban | Without | With | 1,455 | 3.686530 | 3.707446 | 3.162750 |
| Suburban | Without | Without | 1,455 | 3.687307 | 3.707446 | 3.184575 |
| Urban | With | With | 940 | 2.296086 | 1.996680 | 3.645747 |
| Urban | With | Without | 940 | 2.298607 | 1.996680 | 3.657227 |
| Urban | Without | With | 940 | 3.772296 | 3.792186 | 3.645747 |
| Urban | Without | Without | 940 | 3.773831 | 3.792186 | 3.657227 |
| Dense Urban | With | With | 195 | 2.570365 | 2.112632 | 4.127528 |
| Dense Urban | With | Without | 195 | 2.586714 | 2.112632 | 4.187005 |
| Dense Urban | Without | With | 195 | 4.044732 | 4.027505 | 4.127528 |
| Dense Urban | Without | Without | 195 | 4.055141 | 4.027505 | 4.187005 |
