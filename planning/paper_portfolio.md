# Paper portfolio and novelty separation

## Paper A - conference/workshop

Working title: **Height-Aware Attenuation Priors for Dense UAV Channel Knowledge Maps**

Single claim: a training-only, auditable attenuation prior can reproduce stable radial, height, visibility, and morphology structure in dense UAV CKMs without a neural residual model.

Included:

- coherent LoS free-space/two-ray structure;
- height-binned amplitude, phase, bias, and radial calibration;
- morphology-aware NLoS calibration;
- strict city-held-out evaluation;
- attenuation-only RMSE, LoS/NLoS, height, and spatial-correlation diagnostics;
- flat-terrain limitation and non-flat-terrain follow-up.

Excluded:

- HARP-Net architecture and probabilistic residual heads;
- delay-spread and angular-spread priors/results;
- joint multi-task training;
- end-to-end runtime claim;
- journal-scale error-distribution diagnostics.

## Paper B - journal extension

Working title: **HARP-Net CKM: Prior-Anchored Multi-Target Learning for Dense UAV Channel Knowledge Maps**

The attenuation prior is summarized as prior/companion work. The journal's central claim is that a height-conditioned residual model improves strong frozen anchors jointly for attenuation, delay spread, and angular spread on unseen cities while preserving interpretable physical structure.

New contribution groups relative to Paper A:

1. Delay-spread prior and dense-map prediction.
2. Angular-spread prior and dense-map prediction.
3. Shared height-conditioned HARP-Net residual architecture.
4. Distribution-aware/GMM residual training and bounded assembly.
5. Multi-task city/height/visibility diagnostics.
6. Multi-target error-distribution and calibration analyses beyond the attenuation-only map correlation in Paper A.
7. End-to-end runtime comparison and reproducibility record.
8. Non-flat-terrain extension design and evaluation, when implemented.

These groups should comfortably exceed the supervisor's 40% rule by substantive content, but the final overlap must still be checked according to the target journal's policy. New pages alone are not sufficient; the journal needs new methods, experiments, analysis, or data.

## Claim guardrails

- Do not describe ray-tracing agreement as over-the-air validation.
- Do not compare headline numbers as a direct leaderboard when frequency, split, map size, height protocol, or target definition differs.
- State exactly which calibration-side cities were used and that every reported test city is unseen during coefficient fitting and LoS lookup-table construction.
- Keep the geometric LoS/NLoS mask separate from a learned latent class.
- Do not claim non-flat-terrain robustness until it is actually evaluated.
- Keep the conference paper attenuation-only, even if page space remains.

## Work needed before submission

- Add an attenuation-prior ablation: analytic starting structure, height calibration, radial correction, morphology correction, and full prior.
- Confirm the frozen standardized NLoS ridge calibration and its held-out RMSE from committed official-split artifacts.
- Confirm that every table can be regenerated from committed evaluation artifacts.
- Replace draft venue dates with verified live dates.
- Confirm author order, affiliations, acknowledgments, and corresponding author.
- Run IEEE PDF eXpress or the venue's required validator.
- Check overlap and self-citation language after the conference outcome is known.
