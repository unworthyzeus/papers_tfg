# Isolated ITU topology routing ablation

This directory tests an ITU-R P.1410 inspired replacement for the data-quantile
topology routing used by the conference attenuation prior.

The experiment is isolated:

- `run_itu_topology_ablation.py` is a copy of
  `papers_tfg/scripts/run_conference_attenuation_ablation.py`.
- The official script, manuscript, calibrations, and result files are not
  modified.
- All generated files stay under `results/`.
- The Try 74/75 compatible city holdout used by Try 80 remains unchanged.

## Routing

For each unique topology raster:

- `alpha` is the building-covered area fraction.
- `beta` is approximated as four-connected building footprints per square
  kilometre.
- `gamma` is the Rayleigh mode fitted to one mean roof height per connected
  footprint.
- The closest standard environment prototype is selected with equal
  log-ratio distance over `alpha`, `beta`, and `gamma`.

The main `itu3` experiment uses `suburban`, `urban`, and `dense_urban`.
`urban_highrise` is merged into `dense_urban` because its standard prototype
differs mainly in building height and may have limited support. The optional
`itu2` and `itu4` modes are retained as sensitivity checks. No validation or
test city is removed.

Routing is performed independently for every sample from that sample's
topology raster. City identity is used only for the official city holdout
split. A single city can therefore contribute samples to different topology
groups.

The connected-component estimate of `beta` is an approximation because
touching footprints in a raster may be merged. This limitation is exported in
the routing contract and must be stated if the result is reported.

## Commands

Smoke test:

```powershell
python run_itu_topology_ablation.py --routing itu3 --max-fit-maps 300 --max-val-maps 100 --max-test-maps 100 --bootstrap-draws 100 --runtime-maps 10 --out-dir results/smoke_itu3
```

Full official split:

```powershell
python run_itu_topology_ablation.py --routing itu3 --out-dir results/itu3
python compare_results.py
```

The main outputs are:

- `routing_audit.csv`
- `routing_summary.json`
- `nlos_regime_calibration_itu.json`
- `official_test_summary.json`
- `results/comparison/comparison.csv`

## Full official split result

The full `itu3` run completed on the unchanged official split:

| Metric | Current routing | ITU 3 routing | Difference |
| --- | ---: | ---: | ---: |
| Overall RMSE | 1.9277165 dB | 1.9287477 dB | +0.0010312 dB |
| NLoS RMSE | 3.5274650 dB | 3.5350601 dB | +0.0075951 dB |
| Overall MAE | 1.2150736 dB | 1.2170149 dB | +0.0019413 dB |
| NLoS MAE | 2.4703802 dB | 2.4965669 dB | +0.0261866 dB |

LoS metrics are identical because topology routing changes only the NLoS
ridge branch. Seven of the fourteen test cities improve in overall RMSE and
seven worsen. The ITU 3 routing remains better than a single global NLoS ridge
model, but it is marginally worse than the current data calibrated topology
routing. The result does not justify changing the official implementation.

The three training groups contain 4,715 suburban, 5,200 urban, and 925 dense
urban samples. Their median observed building height is approximately 8.9 m,
17.8 m, and 27.3 m respectively, so the dense group is distinct and has enough
training support.
