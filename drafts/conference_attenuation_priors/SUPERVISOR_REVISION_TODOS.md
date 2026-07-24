# Revision TODOs After Supervisor Discussion

Status: waiting for Genia's revised paper and the selected CKM papers.

Do not edit the current paper from this note alone. Use it as the revision
brief once the revised TeX or PDF is provided.

## Intended paper story

The paper should have two main contributions:

1. A UAV CKM dataset addressing the lack of UAV channel data, particularly in
   FR3.
2. A fast and interpretable gain CKM model showing that the dominant structure
   can be captured without a large end to end neural network.

The motivating gaps are:

- limited UAV CKM data, especially in FR3;
- limited availability of fast, transparent CKM predictors;
- extensive use of deep models without always demonstrating that their added
  complexity is necessary for the structure present in the target.

Use restrained language. Do not claim that deep learning is universally
overkill. A defensible formulation is:

> When visibility is available and the dominant channel structure is low
> dimensional, an end to end deep predictor may introduce unnecessary
> complexity. A calibrated analytical baseline can capture the dominant
> structure, leaving deep learning to model residual spatial variation and
> multimodal tails.

## Literature and complexity comparison

- [ ] Read the supplied GLOBECOM 2025 CKM papers.
- [ ] Search for additional recent CKM and radio map prediction papers.
- [ ] Prioritize papers for which computational complexity is directly
      reported or can be computed reliably from a complete architecture,
      released code, or an exact layer table.
- [ ] Select one or two representative deep models that satisfy that
      requirement for the quantitative comparison.
- [ ] Record, when available:
  - parameter count;
  - MACs or FLOPs per output map;
  - inference time and hardware;
  - input information, especially whether visibility is supplied;
  - output resolution;
  - evaluation mask and split protocol.
- [ ] If MACs are not reported, estimate them from the published architecture
      and state that they are estimates.
- [ ] Do not put a paper in the quantitative complexity table when its
      operations cannot be reproduced from the available description. Such a
      paper may still be discussed qualitatively.
- [ ] Do not compare runtime numbers across different hardware as if they were
      direct speedups.
- [ ] Compare all systems at, or normalize them to, the same output resolution
      whenever possible.

For the proposed eight term NLoS model, there are 72 fitted coefficients:
eight coefficients in each of nine regimes. The linear prediction requires at
most eight multiply accumulate operations per evaluated NLoS pixel, but this
does not include feature extraction, visibility generation, routing, or the
LoS prior. Report the complete inference path rather than only the regression
dot product.

## NLoS target structure

The current evidence suggests that, after visibility is supplied, the NLoS
target is comparatively smooth and low dimensional within a map. Most
receivers lie near a dominant continuous level, with a smaller set of
outliers. This helps explain why calibrated linear regression is competitive.

Before writing this claim:

- [ ] Measure the per map NLoS range, standard deviation, interquartile range,
      and outlier share.
- [ ] Aggregate those statistics by topology and transmitter height.
- [ ] Distinguish range in dB, standard deviation in dB, and variance in
      dB squared.
- [ ] Verify and describe the topology mean baseline without relying on one
      representative image.
- [ ] Include a representative NLoS target figure only if its visual pattern
      agrees with the aggregate statistics.

The topology mean and global mean baselines perform almost identically on
final test. Therefore, the current evidence does not show a clear test
advantage from the topology mean alone. Keep the exact values in the
experimental artifact rather than the paper narrative.

## Eight term result

The variant previously described as "only morphology at scale 41" actually
uses geometry and morphology:

\[
\widehat{PL}_{\mathrm{NLoS}} =
w_1 PL_C + w_2 \ell_d + w_3 \delta_{41} + w_4 h_{41}
+ w_5 n_{41} + w_6 \sigma_{\mathrm{sh}} + w_7 \theta_n + w_8.
\]

The included terms are:

- \(PL_C\): calibrated COST231 term;
- \(\ell_d=\ln(1+d_{2D}/1\,\mathrm{m})\);
- \(\delta_{41}\): local building density;
- \(h_{41}\): normalized local building height;
- \(n_{41}\): local fraction of ground NLoS pixels;
- \(\sigma_{\mathrm{sh}}\): angle based shadowing proxy;
- \(\theta_n\): normalized elevation angle;
- bias.

It retains nine coefficient regimes: three topology classes by three
transmitter height bands.

The eight term model recovers **over 90%** of the improvement from the
topology mean baseline to the full model. Use this deliberately conservative
wording in the paper and leave the exact dB values in the repository
artifacts.

## Role of morphology and topology

The strongest supported morphology result is the importance of the 41 pixel
local scale. Removing the 15 pixel family has a negligible effect, whereas
removing the 41 pixel family causes a clearly larger degradation. Keep the
exact differences in the experimental CSV.

Do not currently claim that topology partitioning is one of the two most
important components. The available results show only a modest incremental
gain over the global regression.

The supported wording is:

> The 41 pixel local context is the most informative morphological scale,
> while explicit topology routing provides a smaller additional benefit.

The small conditional NLoS morphology gain does not mean that morphology is
irrelevant. The visibility mask is supplied, so the model already knows which
receivers are obstructed. Morphology may strongly determine the spatial
support of NLoS while changing the attenuation magnitude less after the
receiver is already known to be NLoS.

Also state that \(n_{41}\) is derived from the supplied visibility map. The
eight term variant is not a topology only predictor and is not independent of
ray tracing side information.

## Deep learning positioning

Avoid presenting the result as an argument against deep learning. Present it
as a decomposition:

1. the proposed base captures distance, height, visibility, and dominant local
   morphology;
2. a learned refinement should focus on residual spatial structure, outliers,
   uncertainty, and multimodal distributions;
3. this reduces the burden on the neural network and makes its contribution
   easier to interpret.

Proposed future work statement:

> A following paper will investigate a distribution aware deep refinement of
> the proposed base for path loss, delay spread, and angular spread, with
> explicit treatment of multimodal residuals and rare high value responses.

## Six page plan

- [ ] Keep the dataset and gain CKM model as the two headline contributions.
- [ ] Use one compact related work complexity table.
- [ ] Use one compact ablation table or one concise ablation paragraph.
- [ ] Move full coefficients and extended ablations to the repository.
- [ ] Remove implementation details that do not support the central story.
- [ ] Keep the visibility input and city holdout contract explicit.

## Inputs still needed

- [ ] Genia's revised TeX or PDF.
- [ ] The six GLOBECOM 2025 CKM papers.
- [ ] Any additional CKM papers selected for complexity comparison.
- [ ] Confirmation of which target figure should illustrate the low within map
      NLoS variation.

## Existing supporting artifacts

- `data/official_split_analysis/extended_nlos_ablations/README.md`
- `data/official_split_analysis/extended_nlos_ablations/component_ablation_metrics.csv`
- `data/official_split_analysis/extended_nlos_ablations/recalibrated_models.json`
- `scripts/run_extended_nlos_ablations.py`
