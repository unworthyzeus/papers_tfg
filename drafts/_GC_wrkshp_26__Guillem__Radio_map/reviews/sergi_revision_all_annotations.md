# Revisión de Sergi: transcripción completa de anotaciones

Fuente revisada: `_GC_wrkshp_26__Guillem__Radio_map--SA.pdf`.

Este documento es una transcripción neutral. No interpreta si Sergi tiene razón
ni propone cambios. La capa de anotaciones del PDF contiene 67 elementos:
57 resaltados, 1 tachado y 9 notas de texto. No hay anotaciones independientes
de tipo subrayado, texto de reemplazo, dibujo libre o sello. Cuando una marca
no incluye comentario, se indica explícitamente.

## Página 1

| ID | Tipo | Texto o zona marcada | Comentario de Sergi |
|---|---|---|---|
| S01 | Resaltado | “Its median CPU time is 0.0602 s per map.” | “not sure what this means? is the language standard? Is it an actual metric worth reporting?” |
| S02 | Resaltado | “Uncrewed aerial vehicles” | “(UAVs)?” |
| S03 | Resaltado | “became” | “have become” |
| S04 | Resaltado | Inicio del intervalo “(20 - 80 wavelengths)” | Sin comentario. |
| S05 | Resaltado | “500 m” | “either use ‘m’ or ‘meters’ consistently.” |
| S06 | Resaltado | “20 meters” | Sin comentario; forma parte de la observación S05. |
| S07 | Resaltado | “it is not sufficient.” | “what does this mean? Sufficient for what?” |
| S08 | Tachado | “513×513” en el resumen | Sin comentario. |
| S09 | Resaltado | Espaciado de “10 %” | Sin comentario. |

## Página 2

| ID | Tipo | Texto o zona marcada | Comentario de Sergi |
|---|---|---|---|
| S10 | Resaltado | “compelling” | “employing?” |
| S11 | Resaltado | “Channel Knowledge Map” | “CKM” |
| S12 | Resaltado | “Free-Space” | “free space” |
| S13 | Resaltado | “two-rays” | “two-ray” |
| S14 | Resaltado | Nota al pie: “Note that while the dataset contains attenuation, angular, and delay data, the proposed simulator focuses on predicting only attenuation.” | “not sure if this part of the footnote is needed. The clarification is counterproductive in my opinion, and if needed can be included somewhere else deeper into the text. Also, besides the abstract, this is the first time that the angles are mentioned at alll.” |
| S15 | Resaltado | “Base Station-to-Any” | “??” |
| S16 | Resaltado | “features/layers” | “I would use and stick to one” |
| S17 | Nota | Zona de la figura conceptual del dataset | “would this be an opportunity to introduce part of the notation?” |
| S18 | Nota | Segunda contribución, sobre el marco de predicción | “you may want to separate this into two contributions - proposal of the channel prediciton framework and assessment of its validity, because this would map well with the subsequent sections.” |

## Página 3

| ID | Tipo | Texto o zona marcada | Comentario de Sergi |
|---|---|---|---|
| S19 | Resaltado | “two-rays” | “two-ray” |
| S20 | Resaltado | “construct” | “build” |
| S21 | Resaltado | “1)” de “Building height profile maps...” | “better to itemize to avoid confusion with the subsubsection numbers?” |
| S22 | Resaltado | “2)” de “Binary building occupancy masks...” | Sin comentario; forma parte de S21. |
| S23 | Resaltado | “1)” de “Transmitter height...” | Sin comentario; forma parte de S21. |
| S24 | Resaltado | “2)” de “Classifying tag...” | Sin comentario; forma parte de S21. |
| S25 | Resaltado | “1)” de “Binary visibility mask...” | Sin comentario; forma parte de S21. |
| S26 | Resaltado | “2)” de “Channel attenuation in dB.” | Sin comentario; forma parte de S21. |
| S27 | Resaltado | “3)” de “Multi-path RMS delay spread...” | Sin comentario; forma parte de S21. |
| S28 | Nota | Frase introductoria “We construct a comprehensive benchmark dataset using high-precision deterministic simulations.” | “this introduction sentence does not say much, I would have preferred it to tell me what you are going to describe next” |
| S29 | Resaltado | “H = W = 513” | “is there any reason for choosing 513 and not 256 or others?” |
| S30 | Resaltado | Guion y mayúscula de “Ray-Tracing” | Sin comentario. |
| S31 | Resaltado | Tabla II: “Sample dimensions: 513 m × 513 m” | Sin comentario. |
| S32 | Resaltado | “1 m” | “1-m?” |
| S33 | Resaltado | “RMS” | “should RMS acronym be defined somewhere or is it considered to be known by default?” |
| S34 | Nota | Zona compartida por la Tabla II y la Fig. 2 | “it may be good to not have the table and the figure together. Figure 2 could go to the next page perhaps?” |
| S35 | Resaltado | “γ(m)” en la explicación de los parámetros de topología | Sin comentario. |

## Página 4

| ID | Tipo | Texto o zona marcada | Comentario de Sergi |
|---|---|---|---|
| S36 | Resaltado | “two-rays” | Sin comentario. |
| S37 | Resaltado | “dataset, however,” | “dataset; however,” |
| S38 | Resaltado | “Free-Space Path Loss” | Sin comentario. |
| S39 | Resaltado | “(i.e., ζ̂, ρ̂, φ̂)” antes del cálculo de ζ̂ | Sin comentario. |
| S40 | Nota | Ecuación de `η(h_tx)` | “center it” |
| S41 | Resaltado | “l ∈ {15, 41}” | “??” |
| S42 | Resaltado | “&” en “Baseline & Distance” | Sin comentario. |
| S43 | Resaltado | “clip(θ/90, 0, 1)” | Sin comentario. |
| S44 | Resaltado | “off-line” | “offline” |
| S45 | Resaltado | “branch” en “Line-of-Sight branch” | “Branch” |
| S46 | Resaltado | “branch” en “Non-Line-of-Sight branch” | “Branch” |

## Página 5

| ID | Tipo | Texto o zona marcada | Comentario de Sergi |
|---|---|---|---|
| S47 | Resaltado | “A compact model retaining eight of the 14 features” y el vector reducido `x′ = [Λ_C, ℓ_d, δ_41, h_41, n_41, σ_sh, θ′, 1]^T` | Sin comentario. |
| S48 | Resaltado | “preserves over 90% of the complete model’s improvement over COST 231-Hata model.” | “this appears out of nowhere. How did you obtain this reduced set? Trial and error? Exhaustive search? Is this part of the ablation study? How did you do the ablation study in any case?” |
| S49 | Resaltado | Tabla IV: `513²` | “513x513” |
| S50 | Resaltado | “trained and tested on the exact same data.” | “you mean ‘on the exact same data as our solution’? Otherwise, the text now seems to imply that the same exact data is used both in training and testing.” |
| S51 | Resaltado | Errata “frequencues” | Sin comentario. |
| S52 | Nota | Orden de las subsecciones B y C | “I would normally put the ablation study after the accuracy evaluation and comparison, perhaps before the computational study” |

## Página 6

| ID | Tipo | Texto o zona marcada | Comentario de Sergi |
|---|---|---|---|
| S53 | Resaltado | Tabla V, método propuesto: `513²` | Sin comentario; relacionado con S49. |
| S54 | Resaltado | Tabla V, MATLAB RT: `513²` | Sin comentario; relacionado con S49. |
| S55 | Resaltado | Tabla V, RadioUNet: `256²` | Sin comentario; relacionado con S49. |
| S56 | Resaltado | Tabla V, PMNet: `256²` | Sin comentario; relacionado con S49. |
| S57 | Resaltado | Tabla V, SSL-Radio: `256²` | Sin comentario; relacionado con S49. |
| S58 | Nota | Cabecera y símbolos de la columna “Reported MAC” | “I feel we are missing the * and \cross footnotes?” |
| S59 | Resaltado | Inicio de “∼1 700×” | Sin comentario. |
| S60 | Resaltado | “like-for-like” | “never seen such an expression, would consider rephrasing?” |
| S61 | Resaltado | URL de arXiv añadida a la referencia publicada de RadioUNet | “would remove link” |
| S62 | Resaltado | Enlace DOI de la referencia del dataset IEEE DataPort | “I would remove links for published papers and only keep those that are only in arxiv.” |
| S63 | Resaltado | “channel” en “height-aware channel prediction framework” | “channel attenuation” |
| S64 | Resaltado | “state of the art” usado como adjetivo | “state-of-the-art (it is an adjective here)” |
| S65 | Resaltado | Párrafo que explica el asterisco y la daga de la Tabla V | “should not explain this here, but rather in the table itself.” |
| S66 | Nota | Comparaciones elegidas para la tabla de coste computacional | “why did you compare these here and others in the attenuation accuracy table? Some people may think that you are cherry picking” |
| S67 | Nota | Párrafo de tiempos en CPU | “Would leave a note about these numbers being orientative - in reality, most of these things will be computed using a GPU...” |

## Comprobación de cobertura

- Página 1: S01–S09, 9 elementos.
- Página 2: S10–S18, 9 elementos.
- Página 3: S19–S35, 17 elementos.
- Página 4: S36–S46, 11 elementos.
- Página 5: S47–S52, 6 elementos.
- Página 6: S53–S67, 15 elementos.
- Total: 67 elementos.
