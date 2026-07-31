# Dense Urban NLoS pixel-cap ablation

This isolated experiment tests whether the Dense Urban NLoS ridge models
benefit from more calibration pixels per training map.

It does not modify the released HDF5 file or the existing ITU calibration.
The coherent two-ray LoS branch, radial correction, Suburban coefficients, and
Urban coefficients stay frozen. Only the three Dense Urban antenna-height
regimes are refitted.

The split comes from the official Try 74/75-compatible city-holdout helper used
by Try 80. Candidate caps are selected on Dense Urban validation NLoS RMSE.
Only the selected cap is evaluated on test, together with the frozen 1,024-pixel
baseline.

Run from the repository root:

```powershell
python experiments/itu_dense_urban_more_pixels_ablation/run_dense_urban_pixel_ablation.py
```

Results are written under `results/dense_urban_pixel_caps/`.
