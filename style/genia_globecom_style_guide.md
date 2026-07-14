# Genia + IEEE GLOBECOM writing guide

This guide distills recurring, high-level traits from the archived Evgenii Vinogradov papers and six-page IEEE/GLOBECOM examples. It is a drafting aid, not an instruction to copy phrases or imitate an author's prose verbatim. The source-level observations were checked against the `.tex` examples supplied by Guillem on 2026-07-14.

## Format contract

- Use `\documentclass[10pt,conference]{IEEEtran}` for the workshop/conference manuscript. The supplied sources consistently use IEEEtran conference mode; explicit `twocolumn` is redundant but appears in some older files.
- Design for six two-column pages including references unless the current call explicitly says otherwise.
- Use a compact title that names the object, mechanism, and setting.
- Keep the abstract as one result-led paragraph: problem, missing capability, proposed method, validation setup, main numbers, practical significance.
- Define every acronym on first use and use standard IEEE numbered citations.
- Prefer four to six main sections; avoid thesis-level nesting.
- Make every figure readable at one-column width unless a two-column figure is essential.

## Recurrent argument pattern

1. Open with the system-level motivation in a few sentences.
2. Narrow quickly to the modeling failure that matters for the paper.
3. Name the **state-of-the-art limitation** concretely.
4. State what goes **beyond the state of the art**.
5. Give two to four inspectable contributions.
6. Move to the system/model definition early; do not spend a full page on generic 6G motivation.
7. Tie each modeling choice to either geometry, a cited channel-model structure, or an observed data behavior.
8. End each results paragraph with the engineering meaning of the number.

This pattern is especially visible in Genia's recent spatial-consistency papers: they separate limitations, the proposed advance, contributions, validation, future work, and conclusion with very little rhetorical padding.

## Traits confirmed from the supplied LaTeX sources

- Recent papers usually have five or six main sections: Introduction, model/method, simulator or experimental setup, Results, and Conclusion; Future Work is separated when the limitation deserves more than one sentence.
- Abstracts are a single compact paragraph. The strongest examples follow: application/problem, proposed method, validation environment, quantitative outcome, practical relevance.
- The introduction moves to the exact technical gap quickly. The `3D_beamforming` source makes this explicit with Background, State of the art, Problem statement, and Contributions subsections; newer sources compress the same logic into paragraphs.
- Equations appear only after the physical quantity or decision has been motivated. Symbols are defined immediately around the equation rather than deferred to a notation section.
- Captions say what is shown and state the experimental condition needed to interpret it. Results prose then states the comparison rather than repeating the caption.
- Conclusions repeat the main numerical result and then bound the claim. They do not introduce a new method.
- Some supplied archives include commented alternatives and supervisor markup. Treat the final active prose as evidence; do not reproduce comments, draft fragments, or legacy formatting workarounds.

## Sentence and paragraph style

- Prefer direct subject-verb sentences: “We propose…”, “The model uses…”, “Results show…”.
- Put the claim before implementation detail.
- Use measured comparisons and bounded language: “reduces”, “captures”, “is consistent with”, “under this split”.
- Avoid unsupported adjectives such as “revolutionary”, “perfect”, or “universally applicable”.
- Use short transition phrases that expose logic: “However”, “Consequently”, “In contrast”, “At deployment”.
- Introduce equations with their engineering role, then define every symbol immediately after.
- Use lists only for real enumerations: contributions, model components, or future-work items.

## Abstract template

1. Why the task matters.
2. What current methods miss.
3. “We present/propose…” plus the method in one sentence.
4. Evaluation scope with dataset, split, and principal metric.
5. Two or three concrete results.
6. Practical use or methodological lesson.

Do not put literature review, unexplained acronyms, or promises of future work in the abstract.

## Introduction template for six pages

- Paragraph 1: operational context and why the channel quantity matters.
- Paragraph 2: nearest technical approaches.
- Paragraph 3: exact limitation under the paper's evaluation contract.
- Paragraph 4: proposed answer and why it is different.
- Contributions: two to four bullets, each independently verifiable.
- Final sentence: section roadmap, if space permits.

## Method presentation

- Start from the communication geometry and assumptions.
- Separate literature-derived formula structure from coefficients fitted on this dataset.
- For the attenuation paper, keep LoS and NLoS branches visibly distinct.
- State where the visibility mask comes from and whether it is available at inference.
- State the anti-leakage rule before giving fitted parameters: training cities only; validation for choices; test for final claims.
- Put the full feature inventory in one compact table or equation, not prose scattered across pages.

## Results presentation

- Lead with the held-out protocol, not the best number.
- Report overall and physically meaningful slices (LoS/NLoS, height, city or morphology).
- Give units in table headers or captions.
- Say whether lower or higher is better and define deltas.
- Compare directly only under matching protocols. Otherwise use related work as context.
- State what remains hard. Here, NLoS is the weaker attenuation regime.

## Limitation and future-work language for this project

Use a direct version of the following idea in both manuscripts:

> All current scenes use flat terrain. Therefore, the reported geometry, visibility, and height relationships do not yet account for terrain-induced blockage or changes in local ground elevation. Future work will introduce non-flat digital terrain, compute link geometry relative to local elevation, and test transfer across relief classes.

Do not claim the proposed model already handles non-flat terrain merely because the equations can be generalized.

## Page budget for the attenuation conference paper

| Material | Target space |
|---|---:|
| Title, abstract, index terms | 0.35 page |
| Introduction and related work | 0.9 page |
| Dataset/evaluation contract | 0.65 page |
| LoS and NLoS prior method | 2.0 pages |
| Results and diagnostics | 1.25 pages |
| Limitations, conclusion, references | 0.85 page |

If the paper exceeds six pages, cut background and repeated parameter prose before removing evaluation detail.

## Evidence base in this repository

Highest-weight style references:

- `source_examples/spatially_consistent/main.tex`
- `source_examples/Drone_ID/main.tex`
- `source_examples/3D_beamforming/main.tex`
- `source_examples/Handover/FinalSubmission.tex`

- `vinogradov_2026_icnc_3d_shadow_projections.pdf`
- `vinogradov_2025_probabilistic_los_nlos_segmentation.pdf`
- `vinogradov_pollin_2022_globecom_uav_separation.pdf`
- `colpaert_vinogradov_pollin_2020_globecom_3d_beamforming.pdf`
- `saboor_et_al_2025_random_obstacles_path_loss.pdf`

Venue/dense-map references:

- `lee_et_al_2023_globecom_pmnet.pdf`
- `altenburg_et_al_2024_globecom_workshop_remibrandt.pdf`
- `fenollosa_et_al_2025_globecom_workshop_isac_consistency.pdf`
- GLOBECOM PCMEM6G workshop calls for 2024 and 2025.
