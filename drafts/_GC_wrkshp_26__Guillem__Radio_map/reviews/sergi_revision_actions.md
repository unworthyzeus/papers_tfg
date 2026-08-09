# Revisión de Sergi: diagnóstico y acciones propuestas

Este documento usa los mismos identificadores S01–S67 que
`sergi_revision_all_annotations.md`. La valoración contrasta el PDF anotado con
el modelo y los resultados congelados. **No se presupone que ninguna corrección
de Sergi haya sido aplicada todavía.** Cada entrada indica qué haría sobre la
versión anotada si se acepta la observación.

## Criterio de clasificación

- **Corregir:** hay una errata, ambigüedad real, inconsistencia o afirmación que
  necesita respaldo metodológico.
- **Aclarar:** el contenido es defendible, pero la redacción facilita una lectura
  equivocada.
- **Opcional:** mejora editorial o de maquetación sin efecto técnico.
- **Maquetación:** cambio visual que debe comprobarse en el PDF compilado.
- **Sin cambio técnico:** la formulación es válida; como máximo haría un ajuste
  de estilo para evitar fricción con el revisor.

## Página 1

### S01 — Tiempo de CPU

**Clasificación: Aclarar.** El tiempo sí merece aparecer porque la rapidez es una
de las contribuciones, pero “CPU time” puede confundirse con tiempo acumulado de
procesador. Escribiría algo como: “Median end-to-end inference latency was
60.2 ms per 513×513 map on an AMD Ryzen 5 5600X CPU, with GPU disabled,
excluding file I/O and assuming the visibility mask is available.” En el
resumen se puede abreviar y dejar las condiciones completas en la sección de
complejidad.

### S02 — Definición de UAV

**Clasificación: Corregir.** El resumen debe ser autocontenido. Añadiría
“unmanned aerial vehicle (UAV) base stations” en su primera aparición y usaría
la misma expansión de UAV en todo el artículo. Ahora mismo el resumen y la
introducción no emplean exactamente el mismo término.

### S03 — “became”

**Clasificación: Corregir.** Sustituiría “became” por “have become”, tal como
indica Sergi.

### S04 — Intervalo “20 - 80”

**Clasificación: Corregir.** Escribiría `20--80` en LaTeX para producir el signo
de intervalo correcto, sin espacios alrededor de un guion simple.

### S05 — “500 m” frente a “meters”

**Clasificación: Corregir.** Estandarizaría los valores numéricos con símbolos
SI, por ejemplo `500 m` y `20 m`. “Height in meters” puede mantenerse cuando se
describe semánticamente una variable, porque no es un valor numérico aislado.

### S06 — “20 meters”

**Clasificación: Corregir.** Cambiaría “20 meters” por `20 m`, de acuerdo con
S05.

### S07 — “it is not sufficient”

**Clasificación: Aclarar.** Sustituiría “it is not sufficient” por la carencia
concreta: UrbanRadio3D no proporciona la geometría de transmisor elevado
continuamente variable considerada en este trabajo.

### S08 — Tachado de “513×513” en el resumen

**Clasificación: Sin cambio técnico.** Mantendría el tamaño porque demuestra que
son mapas densos y diferencia el dataset de muchos trabajos de 256×256. Solo lo
eliminaría si fuese imprescindible ahorrar palabras en el resumen. No hay una
inexactitud que obligue a borrarlo.

### S09 — Espacio en “10 %”

**Clasificación: Corregir.** Usaría `10\%` para renderizar `10%` sin el espacio
marcado.

## Página 2

### S10 — “compelling”

**Clasificación: Corregir.** “Compelling” no funciona en esa oración.
Sustituiría por “employing” si conserva el resto de la frase o reescribiría la
oración para evitar una reparación aislada.

### S11 — “Channel Knowledge Map” después de definir CKM

**Clasificación: Corregir.** Usaría “CKM dataset” en la lista de contribuciones,
porque el acrónimo ya está definido y la forma completa vuelve a cargar una
frase larga sin aportar información.

### S12 — “Free-Space”

**Clasificación: Corregir.** Reescribiría la entrada como “free-space path loss”:
minúscula, término completo y guion únicamente porque “free-space” modifica a
“path loss”.

### S13 — “two-rays”

**Clasificación: Corregir.** Cambiaría “two-rays” por “two-ray”.

### S14 — Nota al pie sobre attenuation, AS y DS

**Clasificación: Aclarar y decidir editorialmente.** Sergi no pide directamente
que se elimine la información. Cuestiona que aparezca en esta nota al pie porque
puede debilitar la contribución y porque angular spread y delay spread todavía
no se han introducido suficientemente en el cuerpo del texto. Primero
presentaría con claridad todas las cantidades en la descripción del dataset.
Después elegiría entre dos soluciones: eliminar la nota si el alcance ya queda
claro, o trasladar la aclaración al inicio de la sección del modelo mediante una
frase neutral que indique que este primer benchmark modela attenuation. No
mantendría la formulación defensiva actual en la lista de contribuciones.

### S15 — “Base Station-to-Any”

**Clasificación: Corregir.** “Base Station-to-Any” no es terminología estándar
ni está definida. Lo sustituiría por una descripción directa: la figura muestra
una realización CKM de enlaces desde una estación base UAV hasta receptores
móviles terrestres. Si el dataset no modela movimiento, usaría simplemente
“receptores terrestres” para no atribuirle una movilidad temporal que no contiene.

### S16 — “features/layers”

**Clasificación: Corregir.** Estandarizaría **channels** para las dimensiones de
los tensores `E` y `C`, y reservaría **features** para las variables del vector
de regresión `x`. “Layers” puede quedar solo en lenguaje visual de una figura,
pero idealmente también se sustituiría por “channels”. La versión actual aún
mezcla “environmental layers” y “environmental channels”.

### S17 — Introducir notación en la figura

**Clasificación: Opcional.** Añadiría `E`, `C` y `m` a la figura conceptual o a
su leyenda, con `L=2` y `F=4`, siempre que no la recargue. Esto facilitaría la
transición a la formulación de la sección II, pero no es necesario para la
corrección técnica del trabajo.

### S18 — Separar propuesta y evaluación

**Clasificación: Corregir.** Convertiría la lista en tres contribuciones:
1) dataset, 2) marco de predicción calibrado y 3) evaluación con city holdout,
ablation y comparación de coste. Así la introducción anticipa directamente las
secciones de dataset, modelo y resultados. Si el espacio es crítico, la tercera
contribución puede ser una segunda oración dentro del punto del modelo, pero
debe distinguir claramente propuesta y validación.

## Página 3

### S19 — Segundo “two-rays”

**Clasificación: Corregir.** Cambiaría esta segunda aparición de “two-rays” por
“two-ray”.

### S20 — “construct” frente a “build”

**Clasificación: Sin cambio técnico.** “Construct a dataset” es inglés académico
correcto. “Build” es más directo, pero el cambio es puramente estilístico. Lo
cambiaría solo para seguir la preferencia de Sergi, no por corrección.

### S21 — Numeración de la lista de canales ambientales

**Clasificación: Corregir.** Sustituiría `enumerate` por `itemize` para los
campos del tensor. Los números no expresan orden ni pasos y se pueden confundir
con la numeración de subapartados.

### S22 — Segundo canal ambiental

**Clasificación: Corregir.** Aplicaría el mismo cambio de S21: viñeta en lugar
de “2)”.

### S23 — Primer elemento de metadata

**Clasificación: Corregir.** Usaría viñeta, porque es un campo y no un paso de
un procedimiento.

### S24 — Segundo elemento de metadata

**Clasificación: Corregir.** Usaría viñeta, igual que en S23.

### S25 — Máscara de visibilidad

**Clasificación: Corregir.** Usaría viñeta en la lista de cantidades de canal.

### S26 — Atenuación

**Clasificación: Corregir.** Usaría viñeta, igual que en S25.

### S27 — RMS delay spread

**Clasificación: Corregir.** Usaría viñeta, igual que en S25, y aplicaría además
la definición de RMS propuesta en S33.

### S28 — Frase introductoria del dataset

**Clasificación: Corregir.** La frase actual sigue siendo genérica. La cambiaría
por una oración guía, por ejemplo: “This subsection describes the two
environmental input channels, the four ray-traced channel quantities, and the
metadata distributed with each realization.” Así el lector sabe qué viene a
continuación.

### S29 — Razón de 513

**Clasificación: Aclarar.** Añadiría dos razones breves. El tamaño impar coloca
el transmisor en un píxel central único y permite offsets simétricos de −256 a
256 con una resolución de 1 m. Además, frente a un mapa de 256×256 con la misma
resolución, la mayor extensión captura un entorno urbano más amplio y permite
observar mejor la estructura espacial de la propagación. Por tanto, 513 no es una
elección arbitraria.

### S30 — “Ray-Tracing”

**Clasificación: Corregir.** Usaría “ray tracing” como sustantivo y
“ray-tracing” como adjetivo. En concreto, revisaría la cabecera para que el
compuesto sea coherente con el resto del texto.

### S31 — “Sample dimensions: 513 m × 513 m”

**Clasificación: Corregir.** Separaría conceptos: `Raster size: 513×513 pixels`
y `Horizontal resolution: 1 m`. Evita discutir si la extensión entre centros
de píxel es 512 m o si el área cubierta por celdas se describe como 513 m.

### S32 — “1-m”

**Clasificación: Sin cambio técnico.** Hay dos construcciones correctas. Puede
mantenerse “at a horizontal resolution of 1 m”, sin guion, o reunirse con el
tamaño del raster como “513×513 pixels at 1-m resolution”, con guion porque
`1-m` funciona como adjetivo antepuesto. Preferiría esta segunda versión compacta
si se quiere juntar la información de S31 y S32.

### S33 — RMS sin definir

**Clasificación: Corregir.** Definiría “root-mean-square (RMS) delay spread” en
la primera aparición. Aunque el acrónimo es conocido en telecomunicaciones, la
definición cuesta muy poco y evita la observación.

### S34 — Tabla II y Fig. 2 juntas

**Clasificación: Opcional.** Probaría a colocar la Fig. 2 al principio de la
página siguiente o a separar los floats. No cambiaría contenido por ello y solo
mantendría el movimiento si la versión final de seis páginas queda más legible.

### S35 — Unidades de γ

**Clasificación: Corregir.** Pondría `β [km⁻²]` y `γ [m]` en las cabeceras de la
tabla. Mantendría `α` como adimensional y no pegaría la unidad al símbolo como
`γ(m)`.

## Página 4

### S36 — Tercer “two-rays”

**Clasificación: Corregir.** Cambiaría “two-rays” por “two-ray”.

### S37 — “dataset, however,”

**Clasificación: Corregir.** Separaría las dos proposiciones con punto o punto y
coma: “dataset; however, ...”. Una coma no puede unir correctamente esas dos
oraciones independientes.

### S38 — “Free-Space Path Loss”

**Clasificación: Corregir.** Usaría “free-space path loss” en minúscula en la
prosa y mantendría FSPL como acrónimo de la magnitud.

### S39 — ζ̂ incluida antes de calcularla

**Clasificación: Corregir.** El candidato inicial debe ser el par `(ρ̂, φ̂)`;
después se calcula `ζ̂(ρ̂, φ̂)` y finalmente se conserva el triplete que minimiza
RMSE. No se debe incluir `ζ̂` en el conjunto antes de calcularla.

### S40 — Centrado de la ecuación de η

**Clasificación: Maquetación.** Centraría la ecuación de `η(h_tx)` o la integraría
en el bloque de ecuaciones contiguo, comprobando el resultado en el PDF.

### S41 — Significado de `l ∈ {15, 41}`

**Clasificación: Aclarar.** Definiría `l` como el lado, en píxeles, de una
ventana cuadrada centrada en el receptor. Con resolución de 1 m, son ventanas de
15×15 m y 41×41 m. También definiría explícitamente `W_l(p)` como esa vecindad.

### S42 — Ampersand en prosa

**Clasificación: Corregir.** Cambiaría “Baseline & Distance” por “Baseline and
Distance”.

### S43 — Operador `clip`

**Clasificación: Aclarar.** Definiría una vez
`clip(x,a,b)=min(max(x,a),b)`. Es una operación estándar en código, pero no una
notación matemática universal.

### S44 — “off-line”

**Clasificación: Corregir.** Cambiaría “off-line” por “offline”.

### S45 — “Line-of-Sight Branch”

**Clasificación: Corregir.** Capitalizaría “Branch” en la cabecera.

### S46 — “Non-Line-of-Sight Branch”

**Clasificación: Corregir.** Capitalizaría “Branch” en la cabecera.

## Página 5

### S47 — “eight of the 14 features”

**Clasificación: Corregir.** No lo llamaría “eight of 14 features”. El modelo
completo tiene 14 coeficientes: 13 predictores y el intercepto. El reducido tiene
8 coeficientes: 7 predictores (`Λ_C`, `ℓ_d`, `δ_41`, `h_41`, `n_41`, `σ_sh`,
`θ′`) y el intercepto. Escribiría “an eight-coefficient model using the 41-pixel
morphology scale”.

### S48 — Procedencia del modelo reducido y del “over 90%”

**Clasificación: Corregir.** La descripción anterior como ablation predefinida no
es correcta. La configuración reducida se obtuvo empíricamente mediante *trial
and error*, conservando la geometría y la morfología de 41 píxeles y recalibrando
los coeficientes de cada variación. En el artículo indicaría únicamente que el
modelo de ocho coeficientes conserva más del 90% de la reducción de error del
modelo completo y que ese porcentaje se calcula con los resultados congelados
de test. No incluiría aquí los RMSE intermedios de las variaciones probadas.

### S49 — `513²` en la tabla de precisión

**Clasificación: Corregir.** Cambiaría `513²` por `513×513` para mostrar
explícitamente las dos dimensiones y seguir la convención indicada por Sergi.

### S50 — “trained and tested on the exact same data”

**Clasificación: Aclarar.** Escribiría que el GMM U-Net se entrena con el mismo
split de training y se evalúa en los mismos 2.590 mapas de test y con las mismas
máscaras que la solución propuesta. Así no parece que training y test sean el
mismo conjunto.

### S51 — “frequencues”

**Clasificación: Corregir.** Cambiaría “frequencues” por “frequencies”.

### S52 — Orden de accuracy y ablation

**Clasificación: Corregir.** Movería la ablation después de la evaluación de
precisión y de la comparación, y antes de complejidad. Es el orden más natural:
resultado principal, explicación de componentes y coste.

## Página 6

### S53 — `513²` del método propuesto

**Clasificación: Corregir.** Cambiar a `513×513`, conforme a S49.

### S54 — `513²` de MATLAB RT

**Clasificación: Corregir.** Cambiar a `513×513`, conforme a S49.

### S55 — `256²` de RadioUNet

**Clasificación: Corregir.** Cambiar a `256×256`, conforme a S49.

### S56 — `256²` de PMNet

**Clasificación: Corregir.** Cambiar a `256×256`, conforme a S49.

### S57 — `256²` de SSL-Radio

**Clasificación: Corregir.** Cambiar a `256×256`, conforme a S49.

### S58 — Notas del asterisco y la daga

**Clasificación: Corregir.** Añadiría dentro de la Tabla V, o inmediatamente en
su caption, una nota breve para `*` y `†`. El asterisco indica que el MAC del
método propuesto cuenta solo los productos finales NLOS; la daga indica que el
valor fue reconstruido a partir de la tabla de capas publicada.

### S59 — “∼1 700×”

**Clasificación: Corregir.** Escribiría “approximately 1700×” o
“about 1.7×10³” para evitar una aproximación tipográficamente extraña al inicio
de la cifra.

### S60 — “like-for-like”

**Clasificación: Corregir por claridad.** Sustituiría “like-for-like” por una
frase más corta y directa: “These runtimes are not directly comparable.” La idea
completa puede quedar como: MATLAB RT produce salidas adicionales, por lo que la
diferencia de tiempo es significativa aunque los tiempos no sean directamente
comparables.

### S61 — URL de RadioUNet

**Clasificación: Corregir.** Eliminaría la URL de arXiv porque la referencia ya
incluye la publicación formal en revista. Mantendría autores, título, revista,
volumen, páginas, año y DOI si está disponible.

### S62 — DOI del dataset IEEE DataPort

**Clasificación: Sin cambio técnico.** No aplicaría literalmente la sugerencia a
esta entrada: es un dataset, no un artículo convencional, y su DOI persistente
es precisamente el identificador que debe conservarse. Sí eliminaría URLs
redundantes de artículos ya publicados y mantendría enlaces para datasets,
software, estándares y trabajos disponibles solo en arXiv.

### S63 — “channel” en las conclusiones

**Clasificación: Corregir.** Cambiaría “channel prediction framework” por
“channel attenuation prediction framework”, que refleja exactamente la salida
modelada.

### S64 — “state-of-the-art”

**Clasificación: Corregir.** Escribiría “state-of-the-art models” porque la
expresión funciona como adjetivo compuesto.

### S65 — Explicación fuera de la tabla

**Clasificación: Corregir.** Movería las definiciones de `*` y `†` a la propia
Tabla V, como en S58. El texto posterior debería centrarse en interpretar la
comparación, no en descodificar símbolos.

### S66 — Riesgo de cherry picking entre las dos tablas

**Clasificación: Aclarar.** Explicaría que los baselines de la tabla de
complejidad se eligieron porque sus publicaciones proporcionan dimensiones de
modelo o tablas de capas suficientemente explícitas para calcular el número de
MAC de forma reproducible. Ese es el motivo de que no coincidan exactamente con
los métodos de la tabla de precisión. Una frase breve en el texto o en el caption
evitaría que la selección pareciera arbitraria.

### S67 — Tiempos orientativos y GPU

**Clasificación: Aclarar.** He comprobado que la implementación publicada usa
actualmente NumPy y SciPy, pero el cálculo principal consiste en operaciones
elemento a elemento, filtros de ventana y combinaciones lineales que pueden
implementarse con PyTorch y ejecutarse en GPU. Por tanto, no presentaría el prior
como un método intrínsecamente limitado a CPU. Mantendría en la tabla las
latencias medidas en el mismo Ryzen 5 5600X y explicaría que las reducciones
basadas en el número de MAC son independientes del hardware y, por ello,
transferibles a una implementación en GPU. No afirmaría que el porcentaje exacto
de reducción de tiempo medido en CPU se conserva en GPU sin ejecutar todos los
métodos en la misma GPU, porque la paralelización y el movimiento de memoria
afectan de forma distinta a cada implementación.

## Prioridad sugerida

### Prioridad alta

- S01: definir exactamente la medición de tiempo.
- S14: retirar o recolocar la nota al pie que debilita la historia.
- S16: unificar channels, layers y features.
- S18: separar propuesta y evaluación en las contribuciones.
- S29 y S31: explicar 513 y eliminar la ambigüedad de dimensiones.
- S33: definir RMS.
- S41 y S43: definir la ventana y `clip`.
- S47 y S48: explicar correctamente el modelo reducido y su ablation.
- S50: distinguir explícitamente training de test y la igualdad del protocolo.
- S58, S65 y S66: hacer transparentes las notas y criterios de comparación.
- S67: distinguir entre las latencias CPU medidas, la portabilidad del prior a
  GPU y las reducciones de MAC independientes del hardware.

### Prioridad media

- S02, S11, S21–S29, S31, S33, S41, S43, S52–S61.

### Opcional o sin cambio técnico

- S08, S17, S20, S32, S34 y S62.
