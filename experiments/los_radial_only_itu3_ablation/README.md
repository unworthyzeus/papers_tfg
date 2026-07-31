# Isolated radial only LoS ablation with ITU 3 routing

This experiment tests whether the radial correction is sufficient when the
coherent two-ray parameters are removed.

The tested LoS model is:

```text
PL_LoS = FSPL + r(d2D, hTx)
```

`r` is refitted from `path_loss - FSPL` using valid LoS ground pixels from the
official training cities. It is averaged in 1 m distance rings and 5 m UAV
height bins, smoothed radially, and interpolated at the exact UAV height.
There is no `rho`, `phi`, coherent two-ray correction, or separate two-ray
bias in the fitted artifact or inference path.

The NLoS ridge coefficients and ITU 3 routing are frozen from the previous
isolated experiment. This makes LoS the only changed component. Topology is
still assigned independently for each sample from its topology raster; city
identity is used only for the official holdout split.

All files are local to this directory. The official script, paper,
calibrations, previous ITU experiment, and HDF5 are not modified.

## Commands

Smoke test:

```powershell
python run_los_radial_only_itu3.py --max-fit-maps 300 --max-val-maps 100 --max-test-maps 100 --bootstrap-draws 100 --runtime-maps 5 --out-dir results/smoke
```

Full official split:

```powershell
python run_los_radial_only_itu3.py
python compare_topology_rmse.py
```

The main outputs are:

- `results/radial_only_itu3/los_radial_only_calibration.json`
- `results/radial_only_itu3/official_test_summary.json`
- `results/radial_only_itu3/official_test_per_map_metrics.csv`
- `results/topology_comparison/rmse_by_topology_comparison.csv`

## Full official split result

The full run refitted `r` on all 10,840 official training maps and evaluated
the unchanged 2,590-map test split.

| Model | Overall RMSE | LoS RMSE | NLoS RMSE |
| --- | ---: | ---: | ---: |
| Two ray plus radial correction, ITU 3 NLoS | 1.92875 dB | 1.73704 dB | 3.53506 dB |
| FSPL plus refitted radial correction, ITU 3 NLoS | 3.72924 dB | 3.74435 dB | 3.53506 dB |

The NLoS result is exactly unchanged because its coefficients were frozen.
Removing the coherent two-ray component increases LoS RMSE by 2.00731 dB.
The newly fitted radial profile is therefore not sufficient to replace the
coherent two-ray structure.

### Pixel-weighted RMSE by ITU 3 topology

| Topology | Test maps | Previous overall | New overall | Previous LoS | New LoS | NLoS, both |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Suburban | 1,470 | 1.70101 | 3.68741 | 1.60705 | 3.70839 | 3.16761 |
| Urban | 925 | 2.30086 | 3.77185 | 1.99940 | 3.79144 | 3.64840 |
| Dense urban | 195 | 2.57057 | 4.04486 | 2.11263 | 4.02750 | 4.12827 |

All values are in dB. Building pixels are excluded, and the two runs contain
the same test samples with identical per-sample topology assignments.
