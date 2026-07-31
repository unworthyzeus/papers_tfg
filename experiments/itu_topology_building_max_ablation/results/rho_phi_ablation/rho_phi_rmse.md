# Rho/Phi ablation with fixed ITU topology conditioning

All values are pixel-weighted RMSE in dB on the 2,590 official held-out test maps.
Buildings are excluded. Every variant includes a radial correction `r(d2D, hTx)`
recalibrated on the 10,840 official training maps.

Both rows use the same three topology-specific NLoS ridge calibrations
with per-sample ITU routing. Only rho, phi, and the two-ray bias change.

| Scope | Rho/Phi | Maps | Overall RMSE | LoS RMSE | NLoS RMSE |
|---|---|---:|---:|---:|---:|
| Global | With | 2,590 | 1.928750 | 1.737044 | 3.535074 |
| Global | Without | 2,590 | 3.729239 | 3.744350 | 3.535074 |
| Suburban | With | 1,455 | 1.697705 | 1.604754 | 3.162750 |
| Suburban | Without | 1,455 | 3.686530 | 3.707446 | 3.162750 |
| Urban | With | 940 | 2.296086 | 1.996680 | 3.645747 |
| Urban | Without | 940 | 3.772296 | 3.792186 | 3.645747 |
| Dense Urban | With | 195 | 2.570365 | 2.112632 | 4.127528 |
| Dense Urban | Without | 195 | 4.044732 | 4.027505 | 4.127528 |
