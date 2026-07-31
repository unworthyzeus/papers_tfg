# Official ITU source for alpha, beta, and gamma

The source used by this experiment is
[Recommendation ITU-R P.1410-6, Propagation data and prediction methods
required for the design of terrestrial broadband radio access systems
operating in a frequency range from 3 GHz to 60 GHz](https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.1410-6-202308-I%21%21PDF-E.pdf),
published in August 2023.

The ITU catalogue entry is available on the
[official P.1410-6 recommendation page](https://www.itu.int/rec/R-REC-P.1410-6-202308-I/en).

The recommendation defines the statistical building parameters as follows:

* `alpha`: ratio of land area covered by buildings;
* `beta`: mean number of buildings per square kilometre;
* `gamma`: the variable determining the building-height distribution.

For the proposed Rayleigh height distribution, the recommendation states that
`gamma` is equal to the most probable building height, meaning the mode of the
distribution. Its worked example constructs a cumulative distribution from
rooftop heights and fits the Rayleigh model to that distribution.

The recommendation treats buildings as the observations. It does not specify
how an irregular building-height raster must be reduced to one rooftop height
per footprint. In this project, each four-connected footprint contributes one
observation equal to its maximum raster height. This is a documented raster
adaptation, not wording mandated by ITU-R P.1410-6.
