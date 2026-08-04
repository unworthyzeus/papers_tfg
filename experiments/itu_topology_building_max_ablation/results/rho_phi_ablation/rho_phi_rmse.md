# Rho/Phi ablation with fixed ITU topology conditioning

All values are pixel-weighted RMSE in dB on the 2,590 official held-out test maps.
Buildings are excluded. Every variant includes a radial correction `r(d2D, hTx)`
recalibrated on the 10,840 official training maps.

Both rows use the same three topology-specific NLoS ridge calibrations
with per-sample ITU routing. Only rho, phi, and the two-ray bias change.

| Scope | Rho/Phi | Maps | Overall RMSE | LoS RMSE | NLoS RMSE |
|---|---|---:|---:|---:|---:|
| Global | With | 2,590 | 1.928912 | 1.737044 | 3.536270 |
| Global | Without | 2,590 | 3.729323 | 3.744350 | 3.536270 |
| Suburban | With | 1,455 | 1.697741 | 1.604754 | 3.163216 |
| Suburban | Without | 1,455 | 3.686547 | 3.707446 | 3.163216 |
| Urban | With | 940 | 2.296267 | 1.996680 | 3.646574 |
| Urban | Without | 940 | 3.772406 | 3.792186 | 3.646574 |
| Dense Urban | With | 195 | 2.571558 | 2.112632 | 4.131883 |
| Dense Urban | Without | 195 | 4.045490 | 4.027505 | 4.131883 |
