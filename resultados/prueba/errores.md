# Análisis de errores en prueba (T13)

Errores: 41 (40 FP, 1 FN) de 200 reseñas; umbral 0.0909. Categorías e hipótesis escritas después de la corrida única; no se cambió ninguna etiqueta.

## Resumen por tipo de falla

| Grupo | Tipo de falla | Errores | En los 20 |
|---|---|---|---|
| A | Etiqueta probablemente equivocada según la guía (el modelo detecta una falla que la etiqueta no marcó) | 12 | 7 |
| B | Caso en la frontera de la guía (sabor contra falla, política contra cobro) | 7 | 4 |
| C | Decepción de sabor o precio leída como problema | 2 | 2 |
| D | Reseña positiva o neutral con vocabulario de problemas (espera, logística, ironía, faltas) | 10 | 4 |
| E | Elogio apenas sobre el umbral bajo (0.091): costo aceptado por diseño | 9 | 2 |
| F | Falso negativo: queja corta con negaciones | 1 | 1 |

## Los 20 casos más informativos

### A. Etiqueta probablemente equivocada según la guía (el modelo detecta una falla que la etiqueta no marcó)

| id | Tipo | p | ★ | Paráfrasis | Hipótesis de la causa |
|---|---|---|---|---|---|
| `9c2f133774e1` | FP | 0.865 | 4 | Tardaron muchísimo en traer el platillo; otro mesero lo notó y lo resolvió | Etiqueta probablemente equivocada: problema resuelto en el momento es atender (guía 1.1 y R3) |
| `5c450f8ba59c` | FP | 0.787 | 1 | Todo rico pero a las pocas horas las dos personas tuvieron síntomas de intoxicación | Etiqueta probablemente equivocada: comida en mal estado es atender (D11); el modelo acierta |
| `547e63c6d863` | FP | 0.730 | 1 | Personal cortante y con cara de fastidio; les aventaron la cuenta para que se fueran | Etiqueta probablemente equivocada: trato con un hecho concreto es atender (R3) |
| `17048e2caf03` | FP | 0.637 | 4 | Buen servicio; los sanitarios tuvieron una falla y se saturaron | Etiqueta probablemente equivocada: problema de pasada en una reseña positiva es atender (guía 1.4) |
| `e02b691244bf` | FP | 0.568 | 4 | El gerente los alcanzó en la calle para reclamar una propina que sí habían dejado | Etiqueta probablemente equivocada: trato y propina exigida son atender (R3 y 1.2) |
| `5479afa9ba80` | FP | 0.354 | 3 | Lugar bonito para turistas pero servicio muy lento: 15 minutos por un vaso de agua | Etiqueta probablemente equivocada: espera concreta es atender (R3) |
| `de48193397db` | FP | 0.130 | 4 | Comida rica pero tardaron en darles lugar y las meseras no estaban pendientes | Etiqueta probablemente equivocada: tiempo y servicio con hecho son atender (R3) |

### B. Caso en la frontera de la guía (sabor contra falla, política contra cobro)

| id | Tipo | p | ★ | Paráfrasis | Hipótesis de la causa |
|---|---|---|---|---|---|
| `9c0256e3c898` | FP | 0.533 | 2 | Sabor flojo; el queso ya estaba amargo y la persona que cobra atiende mal | Frontera de la guía: sabor (R1 → 0) contra queso echado a perder y trato (→ 1) |
| `885a3f32e46f` | FP | 0.309 | 1 | Cobran cover y no sirven bebidas sin un consumo mínimo de comida | Frontera de la guía: política anunciada (R2 → 0) contra cobro (1.2 → 1) |
| `4ab363bf366e` | FP | 0.230 | 2 | Pizza con mucho menos ingrediente del anunciado; porciones pequeñas para el precio | Frontera de la guía: precio (→ 0) contra ingrediente anunciado que faltó (R1 → 1) |
| `253da5c8f408` | FP | 0.149 | 2 | Sushi frito en aceite quemado y pescado que no se sentía fresco | Frontera de la guía: ¿juicio de sabor o falla verificable de preparación (R1)? |

### C. Decepción de sabor o precio leída como problema

| id | Tipo | p | ★ | Paráfrasis | Hipótesis de la causa |
|---|---|---|---|---|---|
| `ed55ae2ad450` | FP | 0.393 | 2 | Decepción con el sabor de la pizza y la pasta para ser un restaurante italiano | Modelo confunde decepción de sabor (R1 → 0) con un problema: aprendió que tono negativo ≈ atender |
| `3cf9a28ac835` | FP | 0.195 | 3 | Comida vegana con poco sabor y cara para el tamaño; el personal muy amable | Modelo confunde opinión de precio y sabor con un problema |

### D. Reseña positiva o neutral con vocabulario de problemas (espera, logística, ironía, faltas)

| id | Tipo | p | ★ | Paráfrasis | Hipótesis de la causa |
|---|---|---|---|---|---|
| `fbc35407bb9b` | FP | 0.594 | 5 | Reseña positiva, sin mayúscula inicial, que lista acompañamientos y venta para llevar | Vocabulario de logística (para llevar; venden salsas) que en entrenamiento acompaña quejas de entrega; texto con signos raros |
| `06c3a9c9cb0f` | FP | 0.529 | 4 | Tortería tradicional: no se paga por la porción sino por la historia; mejor pedir para llevar | Ironía y comparación con el precio que el modelo lee como queja |
| `51f03829f7e2` | FP | 0.373 | 5 | Positiva y nostálgica con varias faltas de ortografía | Faltas de ortografía y redacción poco común: n-gramas desconocidos |
| `203309e22830` | FP | 0.127 | 5 | Muy rico todo; "consideren que sólo hay un cocinero" | Reseña muy corta con una advertencia que suena a queja de tiempo sin serlo |

### E. Elogio apenas sobre el umbral bajo (0.091): costo aceptado por diseño

| id | Tipo | p | ★ | Paráfrasis | Hipótesis de la causa |
|---|---|---|---|---|---|
| `61f2adcd3c85` | FP | 0.095 | 5 | Lugar bonito y relajado, comida muy buena | Elogio puro apenas sobre el umbral: el umbral 0.09 manda al gerente casos con p ≈ 0.1 a propósito |
| `120e961de8f6` | FP | 0.092 | 5 | Elogio a la comida y al mesero; les dieron pastel de cumpleaños | Elogio puro apenas sobre el umbral (p = 0.092 contra 0.091): costo aceptado del umbral bajo |

### F. Falso negativo: queja corta con negaciones

| id | Tipo | p | ★ | Paráfrasis | Hipótesis de la causa |
|---|---|---|---|---|---|
| `adcac2dd2742` | FN | 0.018 | 3 | Local pequeño; servicio malo y tardan mucho en atender; sólo hay botana | Único falso negativo (p = 0.018): queja corta y redactada con negaciones ("no es bueno", "no hay") que el modelo no capta |

