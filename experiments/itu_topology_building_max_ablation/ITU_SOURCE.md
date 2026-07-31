# Official ITU source for alpha, beta, and gamma

The source used by this experiment is
[Recommendation ITU-R P.1410-6, Propagation data and prediction methods
required for the design of terrestrial broadband radio access systems
operating in a frequency range from 3 GHz to 60 GHz](https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.1410-6-202308-I%21%21PDF-E.pdf),
published in August 2023.

The ITU catalogue entry is available on the
[official P.1410-6 recommendation page](https://www.itu.int/rec/R-REC-P.1410-6-202308-I/en).

The definitions are in Section 2.1.4, "Statistical model", on printed page
10 of the recommendation, which is page 12 in a normal PDF viewer. It defines
the statistical building parameters as follows:

* `alpha`: ratio of land area covered by buildings;
* `beta`: mean number of buildings per square kilometre;
* `gamma`: the variable determining the building-height distribution.

For the proposed Rayleigh height distribution, the recommendation states that
`gamma` is equal to the most probable building height, meaning the mode of the
distribution. Its worked example constructs a cumulative distribution from
rooftop heights and fits the Rayleigh model to that distribution.

The current P.1410-6 recommendation does not itself tabulate the four exact
environment tuples used here: Suburban `(0.1, 750, 8)`, Urban
`(0.3, 500, 15)`, Dense Urban `(0.5, 300, 20)`, and Urban High-rise
`(0.5, 300, 50)`. Those values are reproduced as "Built-up Parameters for
standard environments" in Table 2 of
[Saboor et al., *A Geometry-Based Modelling Approach for the Line-of-Sight
Probability in UAV Communications*](https://imec-publications.be/bitstreams/0b904d1a-eaf3-4112-aecb-6eda2b35a2d9/download),
printed journal page 367, which is PDF page 4. That paper cites ITU-R P.1410-6
for the built-up statistical model. Therefore, this experiment describes the
tuples as ITU-based rather than claiming that the current recommendation
contains that exact table.

For additional context, P.1410-6 printed page 11 (PDF page 13) gives broad
suburban-to-high-rise ranges for `alpha` and `beta`, and printed page 13 (PDF
page 15) gives a Malvern example with `alpha = 0.11`, `beta = 750`, and
`gamma = 7.63`.

The recommendation treats buildings as the observations. It does not specify
how an irregular building-height raster must be reduced to one rooftop height
per footprint. In this project, each four-connected footprint contributes one
observation equal to its maximum raster height. This is a documented raster
adaptation, not wording mandated by ITU-R P.1410-6.
