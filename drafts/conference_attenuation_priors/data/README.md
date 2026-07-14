# NLoS calibration audit artifacts

- `frozen_nlos_regime_calibration.json`: frozen Try-78 NLoS calibration used by the final Try-80 prior; SHA-256 `055ec1256cd89f576597bd8e9a669d9d81c5a538f3559c0cd6116f88ed6fa90b`.
- `nlos_exact_coefficients.csv`: the nine NLoS regime vectors (three topology classes × three antenna-height classes, with all 15 features).
- `nlos_test_term_audit.csv`: pixel-weighted mean coefficient, feature, signed contribution, and absolute contribution for each regime and topology aggregate.
- `attenuation_audit_metrics.json`: audit selection metadata.

The term audit used every tenth map after sorting the 2,590 final-test maps by the fixed city list and sample name: 259 maps and 3,031,586 valid NLoS receiver pixels. It is a deterministic scale/conditioning diagnostic, not an ablation or a replacement for the full-test performance metrics.

Regenerate from the repository root with:

```powershell
python scripts\analyze_nlos_terms.py --terms-only --stride 10 --log-every 25
```

The script reads the original HDF5 data and imports the exact feature implementation from `Final_Code_TFG`; these large/external inputs are not duplicated here.
