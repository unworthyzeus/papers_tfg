# TFG paper portfolio

Private working repository for papers derived from the HARP-Net CKM thesis. The material is split so that the conference paper can stand on its own and a later journal manuscript can add substantial new contributions without duplicating the conference article.

## Current manuscripts

- `drafts/conference_attenuation_priors/`: six-page IEEE conference/workshop draft focused only on the height-aware attenuation priors.
- `drafts/journal_harpnet/`: 10--13-page-target journal extension covering the multi-target HARP-Net CKM residual model, delay spread, angular spread, diagnostics, and runtime. The attenuation prior is intentionally summarized rather than re-derived.

Both drafts explicitly state a newly recorded limitation: all current simulations assume flat terrain. Follow-up work will incorporate non-flat terrain and test how terrain relief changes visibility, prior calibration, and generalization.

## Supporting material

- `planning/supervisor_paper_plan.md`: Genia's paper-only advice, venue options, and submission sequence from the supplied messages.
- `planning/paper_portfolio.md`: contribution split and journal-extension guardrails.
- `style/genia_globecom_style_guide.md`: an evidence-based writing and formatting guide distilled from archived papers and the supplied GLOBECOM LaTeX sources. It describes reusable traits; it does not copy wording.
- `references/`: openly accessible study copies, official venue calls, supplied `.tex`/`.bib` examples, source URLs, page counts, and checksums.
- `scripts/build_all.ps1`: local LaTeX build helper.
- `scripts/analyze_nlos_terms.py`: reproducible audit of the NLoS multilinear-regression coefficients, feature means, term contributions, and map-correlation definition.
- `scripts/generate_conference_nlos_figure.py`: regenerates the LoS/NLoS comparison directly from the frozen priors and an unseen Vancouver test map.

## Build

From the repository root:

```powershell
.\scripts\build_all.ps1
```

The manuscripts use `IEEEtran`: conference mode for the six-page draft and journal mode for the extension. Before submission, confirm the exact 2026 venue rules, copyright notice, author affiliations, and page policy on the live venue site.
