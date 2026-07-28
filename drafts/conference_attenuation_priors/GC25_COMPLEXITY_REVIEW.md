# Review of the GLOBECOM 2025 Papers and Genia's Revision

Status: literature screened, computable comparisons identified, and the
revised TeX audited. This note does not modify the conference paper.

## Main conclusion

The supplied literature supports a clear but restrained story:

1. Current radio map work often uses U-Nets, variational autoencoders,
   transformers, masked autoencoders, Gaussian processes, or iterative
   diffusion models.
2. Most of the six GLOBECOM papers do not report enough architectural detail
   to reconstruct their operation count reliably.
3. SSL-Radio is the strongest quantitative comparator among the six papers
   because it publishes a complete layer table. GenSpectraLM can also be used
   if every conventional ViT assumption is stated beside the estimate.
4. PMNet remains the cleanest additional neural comparator because its
   convolutional architecture can be executed and counted directly.
5. The contribution should not be framed as "deep learning is unnecessary."
   The defensible claim is that a supplied visibility mask and a calibrated
   physical base explain most of the stable structure. A learned model can
   then focus on residual spatial variation, outliers, uncertainty, and the
   output distribution.

The eight term NLoS variant recovers **over 90%** of the improvement from a
constant regime baseline to the complete NLoS model. The paper narrative
should use that deliberately conservative wording and should not list the
small dB differences between reduced variants.

## Audit of `main_genia.tex`

The revision improves the high level positioning by making the dataset and
the fast interpretable CKM model the two headline contributions. It is not yet
submission ready.

### Blocking editorial items

- The compiled draft is seven pages. Page seven contains only the final two
  references, but missing bibliography records mean the final bibliography may
  become longer.
- The abstract begins with the literal text `PLACEHOLDER> > >`.
- The dataset table contains `Number of Map & ?`.
- The paper organization paragraph contains four `Section ??` placeholders.
- Eleven citation keys are unresolved against the current repository
  bibliography: `Vinogradov2018`, `Geraci2022ntn`, `Zeng2024`, `zeng2021ckm`,
  `Chen2017rem`, `Cui2024`, `saboor26`, `vinogradov2026upsim`, `Bernard2022`,
  `Che2024globfp`, and `Zhu2025atlas`.
- The introduction still says `Air-to-Ground (A2G)`, although the requested
  terminology change was to remove A2G throughout the paper.
- The PDF metadata title contains `adn` instead of `and` and its author order
  does not match the displayed author order.

The seven page observation comes from compiling a temporary copy with the
current repository figures and bibliography. The downloaded source itself was
not edited.

### Claims that need evidence or softer wording

The introduction currently says that dense attenuation prediction generally
uses "heavy, over-parameterized" convolutional networks, that such models
assume fixed terrestrial geometries, and that they often require local fine
tuning in unseen topologies. The six supplied papers show that complex learned
architectures are common, but they do not establish all three statements as
universal limitations.

A safer replacement would be:

> Recent radio map estimators use increasingly expressive convolutional,
> transformer, variational, and diffusion architectures. These models are
> valuable when sparse observations or unresolved propagation effects must be
> inferred, but their added complexity is not always quantified against a
> calibrated analytical baseline. This comparison is especially relevant when
> geometric visibility is already available and the dominant attenuation
> structure is low dimensional.

The claim of robust zero shot generalization is supported only under the
paper's exact contract: unseen cities, the same frequency and raster format,
and a supplied ray traced visibility mask. Those conditions must remain next
to the claim.

### Six page cut strategy

The cleanest cut is not to remove the evidence for the main claim. Instead:

- compress the dataset description and merge the two dataset tables if both
  remain;
- replace the full coefficient tables with one compact reduced model or
  complexity table;
- keep only the ablation result needed for the story and move all coefficients
  and extended reductions to the repository;
- shorten the denominator discussion while retaining the facts that building
  pixels are excluded and that the valid target subset is LoS dominated;
- shorten implementation details already reproducible from the repository;
- keep the CPU runtime qualification and the visibility dependency explicit.

## Screen of the six supplied papers

| Paper | Main method | Complexity information available | Quantitative use here |
|---|---|---|---|
| [TSRDiff: A Diffusion Framework for Accurate Fine-Grained Radio Map Reconstruction](https://doi.org/10.1109/GLOBECOM59602.2025.11432702) | Two conditional diffusion stages, first coarse and then fine, both using U-Net based noise predictors | Reports 150 diffusion steps, RTX 6000 Ada training, 50 epochs, and batch size 8. It omits the full channel schedule, attention width, MLP width, and inference time. | Qualitative only. The method requires repeated network evaluations. Inferring roughly 150 reverse evaluations per stage is reasonable from the stated schedule, but an exact MAC count is not. |
| [RO-HMTGP: Land Feature Aware Radio Environment Map Construction](https://doi.org/10.1109/GLOBECOM59602.2025.11432161) | Heterogeneous multitask Gaussian process with two outputs, linear model of coregionalization, and three spectral mixture latent functions | Gives data set sizes, batches of 500 samples, and 100 optimization steps, but no end to end inference time or sufficient implementation detail for a per map operation count. | Asymptotic discussion only. Dense GP factorization is cubic in the batch size without further approximation, but this is not a fair measured comparison to dense map inference. |
| [GenSpectraLM](https://doi.org/10.1109/GLOBECOM59602.2025.11431695) | ViT based masked spectrum model with a 12 block encoder and an 8 block decoder | Reports encoder and decoder dimensions, block counts, and attention heads. Patch size and feed forward expansion are application dependent or unstated. | Quantitative estimate only when the patch size, input channels, masking ratio, and feed forward ratio are stated explicitly. |
| [RadioVAE](https://doi.org/10.1109/GLOBECOM59602.2025.11432712) | Twenty layer U-Net inside a variational autoencoder, with Monte Carlo dropout for probabilistic maps | Does not specify all channel widths, latent dimension, skip wiring, number of stochastic passes, hardware, or inference time. | Qualitative only. Its cost necessarily includes multiple stochastic forward passes when uncertainty is sampled, but the multiplier is not reported. |
| [SSL-Radio](https://doi.org/10.1109/GLOBECOM59602.2025.11431663) | Twenty layer encoder decoder for 256 by 256 radio maps with self supervised pretraining | Publishes a layer table with resolutions, channel counts, and kernel sizes. Skip concatenation is described but its precise wiring is not fully tabulated. Experiments use an RTX 3090 and Intel Xeon, with no inference time. | Best supplied quantitative comparator. Parameters and convolutional MACs can be bounded under two transparent skip interpretations. |
| [KR-MAE](https://doi.org/10.1109/GLOBECOM59602.2025.11432291) | Distribution aware masked autoencoder with KL divergence, Gaussian mixture modeling, and focal loss | Omits the patch size, token dimension, number of blocks and heads, decoder design, mixture count, hardware, and inference time. | Qualitative only. It is useful for the distribution aware future work motivation, not for an operation count. |

These papers also solve different observation problems. Several reconstruct a
map from sparse radio measurements, whereas the proposed prior receives a
building map, transmitter height, and a complete visibility mask. Complexity
can be compared, but accuracy must not be ranked without stating this
difference.

## Additional papers screened for reproducible complexity

- [PMNet](https://arxiv.org/abs/2211.10527) is the best additional comparator.
  It directly predicts dense path loss, its architecture can be reconstructed,
  and it is already relevant to the conference paper's related work. The
  executable project reconstruction is used for the count below.
- [RadioUNet](https://github.com/RonLevie/RadioUNet) has public implementation
  code and is therefore countable in principle. It is not needed in the compact
  paper table if PMNet is retained, because the two rows would represent the
  same broad convolutional family while consuming scarce space.
- [RadioDiff](https://github.com/UNIC-Lab/RadioDiff) also publishes code, but
  its total inference cost depends on the selected sampler, number of denoising
  evaluations, latent resolution, and checkpoint configuration. It should
  remain a qualitative example unless one frozen configuration is profiled end
  to end.

This selection rule is intentional: public code or a complete layer table is
more useful for the complexity claim than a newer model whose widths, token
counts, or sampling schedule cannot be reconstructed.

## Reconstructable computation estimates

One MAC denotes one multiplication followed by one accumulation. The FLOP
figures below use the common convention of two FLOPs per MAC. Only the PMNet
and analytical prior rows were obtained from executable project code. The
other neural rows are paper based estimates.

| Model | Output used for count | Parameters or stored calibration | MACs per map | Evidence level |
|---|---:|---:|---:|---|
| Proposed prior with eight term NLoS regression | 513 by 513 | About 66.8 thousand LoS calibration entries plus 72 NLoS coefficients | NLoS dot product averages about 96.9 thousand MACs on the final test set and is bounded by 2.11 million MACs if evaluated at every pixel | Exact dot product count; full estimator also includes feature extraction, transcendental functions, lookup, clipping, and routing |
| PMNet, output stride 8 | 256 by 256 | 33.34 million | 52.71 GMAC, or 105.42 GFLOPs | Counted from the executable convolutional architecture; convolution and transposed convolution only |
| PMNet, output stride 16 variant | 256 by 256 | 33.34 million | 31.44 GMAC, or 62.87 GFLOPs | Same counting method, included as a sensitivity bound |
| SSL-Radio | 256 by 256 | About 15.4 to 20.4 million | About 16.9 to 21.9 GMAC | Range spans a sequential lower interpretation and conventional concatenative U-Net skips |
| GenSpectraLM | 224 by 224 | About 111.1 million | About 9.51 GMAC | Estimate assuming one input channel, 16 by 16 patches, 75% masking, and a feed forward ratio of four |
| GenSpectraLM extrapolation | 512 by 512 | Same parameters | About 57.6 GMAC | Same assumptions, with attention recomputed for 1024 total tokens and 256 visible encoder tokens; not a paper reported configuration |

### What the proposed prior count does and does not mean

There are 31,365,314 valid NLoS receivers across 2,590 final test maps, or
about 12,110 per map. Eight coefficients therefore require about 96,900 MACs
per average map. A deliberately loose full grid upper bound is

\[
513^2 \times 8 = 2{,}105{,}352\ \text{MACs}.
\]

That number is only the final NLoS linear combination. The complete method
also computes the coherent LoS prior, radial residual lookup, distance and
angle transforms, three 41 pixel local statistics, mask routing, and clipping.
It is therefore incorrect to divide a neural model's GMAC count by 96,900 and
call the result an end to end speedup.

The complete current prior has an audited CPU median of 0.0602 seconds per map
on an AMD Ryzen 5 5600X. The MATLAB ray tracer audit uses the same CPU and has
a 102.289 second median, but the raw ratio is not a like for like algorithmic
speedup because the ray tracer additionally generates visibility, delay
spread, and angular spread. Both timing results are CPU only.

The stored LoS state needed by the current predictor contains 91 height bins,
three 91 element two ray parameter arrays, a 91 by 363 smoothed residual
table, its support counts, and a 363 element fallback profile. This is about
66.8 thousand numeric entries, excluding calibration diagnostics that are not
needed for deployment. The reduced NLoS branch adds 72 fitted coefficients:
eight coefficients in each of nine regimes.

### Counting assumptions for neural models

The PMNet hook count includes `Conv2d` and `ConvTranspose2d` operations. It
does not count batch normalization, activations, pooling, interpolation, or
memory movement. The same omission should be kept when comparing convolution
MAC estimates.

For SSL-Radio, the published layer table is sufficient to reproduce the main
convolutions, but it does not fully specify the input channel count and every
skip connection. The lower estimate uses two input channels and the listed
layers sequentially. The upper estimate uses conventional concatenative
U-Net skips and four input channels. The range is more honest than one falsely
exact number.

For GenSpectraLM, standard transformer accounting was used:

\[
\mathrm{MAC}_{\mathrm{block}} \approx 12ND^2 + 2N^2D,
\]

where the first term covers attention projections and an MLP expansion ratio
of four, and the second covers the two attention matrix products. The paper
does not fix the patch size or MLP ratio for every application, so these
figures must always be labeled as estimates.

## Recommended scientific story

### Contribution and gap

The paper can credibly make these two contributions:

1. A dense UAV CKM data set for FR3 with varied transmitter heights and strict
   city holdout evaluation.
2. A transparent, height aware attenuation prior that produces a full dense
   map quickly when geometric visibility is available.

The modeling gap is not simply that other work is "too complex." It is that
model complexity is rarely isolated from the stable physical structure and
is often not reported in a reproducible way. The proposed work supplies a
strong analytical base against which learned refinement can be measured.

### NLoS statement

Use this wording only after the aggregate per map statistics are complete:

> Conditional on the supplied visibility mask and calibration regime, much of
> the NLoS attenuation within a map follows a smooth, low dimensional trend,
> with a smaller set of locally difficult or outlying receivers. This explains
> why a compact calibrated regression captures most of the improvement over a
> constant regime baseline.

Avoid saying that a single image proves low NLoS variance or that the output
is easy in general. The claim is conditional on visibility, frequency,
calibration regime, and this data set.

### Eight term statement

Recommended paper sentence:

> A reduced eight term NLoS model retains the 41 pixel context together with
> range, elevation, visibility, COST231, and bias terms. After independent
> recalibration in the same nine regimes, it recovers over 90% of the complete
> model's improvement over the constant regime baseline.

Do not call this variant "morphology only." Its terms are

\[
PL_C,\ \ell_d,\ \delta_{41},\ h_{41},\ n_{41},\
\sigma_{\mathrm{sh}},\ \theta_n,\ 1,
\]

and `n_41` is derived from the supplied visibility map.

### Topology interpretation

The present ablation supports the importance of 41 pixel local context. It
does not support describing topology partitioning as the second dominant
component: removing topology routing causes only a modest change once the
other spatial and visibility features remain. The stronger statement is:

> The 41 pixel context is the most informative local scale. Regime specific
> calibration provides a smaller additional adjustment, while much of the
> apparent morphology dependence is already encoded by the supplied
> visibility map and local descriptors.

If topology partitioning is to become a headline result, add a dedicated
ablation that compares the same eight features with global, height only,
topology only, and nine regime calibration, and report NLoS metrics rather
than relying on the LoS dominated aggregate.

### Role of deep learning

Recommended transition:

> The result motivates a prior first learning strategy rather than a rejection
> of deep models. The analytical component captures repeatable range, height,
> visibility, and morphology structure. A learned residual model can then
> concentrate its capacity on local deviations, rare responses, and
> multimodal uncertainty instead of relearning the complete attenuation field.

Recommended future work sentence:

> A future journal paper will investigate a distribution aware deep refinement
> of this base for path loss, delay spread, and angular spread, explicitly
> modeling multimodal residuals and rare high value responses.

## Recommended quantitative comparison for the paper

For a six page paper, use at most three comparison rows:

1. the proposed prior, with measured CPU latency and an explanation of what is
   included;
2. PMNet, with the executable parameter and convolution MAC count;
3. SSL-Radio, labeled as an estimate from its published layer table.

GenSpectraLM is useful as an optional transformer example, but its count
depends on assumptions. The diffusion, VAE, MAE, and GP papers should be cited
as examples of method families, not placed in an exact operation table.

Accuracy from these papers should not share a ranking table with the proposed
prior because the observation contract, resolution, split, frequency, target,
and masks differ. The complexity comparison is about architectural burden,
not a claim that the proposed error is directly better.

## Remaining evidence TODOs

- Compute per map NLoS standard deviation, interquartile range, robust range,
  and outlier share, then aggregate by topology and transmitter height.
- Select a representative NLoS target map only after checking that it agrees
  with those aggregate statistics.
- Decide whether the reduced eight term model replaces the fourteen term model
  in the paper or is presented only as an ablation.
- Measure the end to end runtime of the reduced feature path if it is
  implemented as the deployed model. The current 0.0602 second audit measures
  the complete current prior.
- Recompile Genia's revision with the intended Overleaf bibliography and cut it
  to six pages after every reference resolves.

## Reproducibility pointers

- Extended recalibrated ablations:
  `data/official_split_analysis/extended_nlos_ablations/README.md`
- Exact variant metrics:
  `data/official_split_analysis/extended_nlos_ablations/component_ablation_metrics.csv`
- Recalibrated coefficients:
  `data/official_split_analysis/extended_nlos_ablations/recalibrated_models.json`
- PMNet executable reconstruction used for the count:
  `C:/TFG/TFGpractice/weird_tries/test_weird_tries_pmnet.py`
- Current LoS prior and deployed calibration access:
  `C:/TFG/TFGpractice/TFGSeventyEighthTry78/prior_try78.py`
