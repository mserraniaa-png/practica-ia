# Plan — Práctica 1: ¿esta reseña de restaurante hay que atenderla?

Enunciado y rúbrica: [INSTRUCCIONES.md](INSTRUCCIONES.md). Decisiones: [DECISIONES.md](DECISIONES.md). Entrega: **lunes 30-nov-2026, 23:59 (CDMX)**.

## El caso

Un restaurante (o una cadena) recibe reseñas en Google Maps y nadie alcanza a leerlas todas. La aplicación lee **el texto de una reseña** de cualquier restaurante y responde si **reporta un problema que el negocio debe atender**, con su probabilidad y el umbral aplicado.

- **Dominio:** lenguaje sin modelos de lenguaje. Modelo entregado: TF-IDF + capas densas. Alternativa a comparar: LSTM con embeddings propios. Sin embeddings ni modelos preentrenados en el clasificador.
- **Clases (binario):** `atender` = reporta un problema concreto que el negocio puede corregir (servicio, higiene, cobro, tiempo, comida en mal estado…) / `no_atender` (elogio, opinión de gusto, queja vaga, sugerencia, comentario neutro). Criterios completos en D11.
- **La etiqueta no son las estrellas:** un 4★ con "el baño estaba sucio" es `atender`; un 2★ con "caro pero rico" es `no_atender`. Las estrellas sólo se usan en un baseline; la app recibe únicamente el texto.
- **Costos (D2):** FP = 3 min de gerente; FN = 30 min. Se reporta el costo esperado en minutos por cada 1000 reseñas.
  - Si las probabilidades están bien calibradas, el umbral óptimo teórico es 3 / (3 + 30) ≈ **0.09**. Comparar el umbral del barrido con este valor sirve para decir si la probabilidad sirve para decidir o sólo para ordenar.
  - Referencia con ~25 % de quejas: "nada es atender" cuesta ~7,500 min/1000 y "todo es atender" ~2,250 min/1000. El baseline trivial que hay que vencer es el más barato de los dos, no la clase mayoritaria.

## Datos

- **Fuente:** Google Places API (New), restaurantes de CDMX. Hasta 5 reseñas "más relevantes" por lugar → muchos restaurantes con pocas reseñas cada uno.
- **Descargado:** 2,783 reseñas de 562 restaurantes, $0 (ver *Avance*). Se conservan (D1).
- **Campos:** `id`, `lugar` (id corto), `consulta`, `tipo_lugar`, `rating_lugar`, `fecha`, `estrellas`, `idioma`, `texto` (`originalText`, anonimizado), `etiqueta`. Sin autor ni foto.
- **Etiquetado:** 700 reseñas (200 validación + 200 prueba aleatorias; 300 entrenamiento, mitad de 1–3★) (D4). Una sola persona, a mano, con la guía escrita antes de empezar y el tiempo registrado. **Ninguna etiqueta la propone un LLM ni otro modelo.**
- **Split temporal (D3, D5):** entrenamiento < 1-jul-2026 · validación jul–sep · prueba ≥ 1-oct. Los restaurantes de prueba no aparecen en validación ni en entrenamiento, y los de validación no aparecen en entrenamiento. Prueba intocada hasta la corrida única.
- **Términos de Google:** las reseñas no se publican ni se suben al repo (`.gitignore`). Para reproducir se entrega una muestra sintética con la misma estructura.
- **Plan B:** reseñas de Steam (`IUserReviewsService/GetAppReviews`, sin key, `languages[0]=latam|spanish`), pregunta "¿reporta un problema técnico?". Ya probado. Hoy no hace falta.

## Revisión del plan frente al enunciado

### Primera revisión (23-nov): brechas y dónde quedaron resueltas

| # | Brecha | Resuelta en |
|---|---|---|
| 1 | Registro de decisiones con cifra y alternativa (criterio 5) | `DECISIONES.md`, T16 |
| 2 | Costos en unidades | D2 |
| 3 | El sobremuestreo sesga el costo por 1000 | D4: sobremuestreo sólo en entrenamiento |
| 4 | Mismo restaurante en varios splits | D5 |
| 5 | Prueba con menos de 20 errores | D8, T13 |
| 6 | Corrida única sin candado | T12 |
| 7 | La muestra sintética no existe (el README dice que sí) | T6 |
| 8 | Que funcione fuera de mi máquina | T11: contenedor Docker (ADR-08) |
| 9 | Caso nuevo para el video | T15 |
| 10 | Medir < 2 s y probar entradas raras | T10 |
| 11 | Fuera de dominio de un solo tipo | D9, T14 |
| 12 | Medir el cómputo (< 20 min) | T7, T8, T12 |
| 13 | Calendario sin holgura | Calendario abajo |
| 14 | Consistencia de una sola etiquetadora (opcional) | T5 |

### Segunda revisión (23-nov): brechas nuevas

| # | Brecha | Riesgo | Resuelta en |
|---|---|---|---|
| 15 | **El baseline "clase mayoritaria" no es el trivial más barato.** Con FN = 10 × FP, "todo es atender" cuesta ~3 veces menos que "nada es atender". Si sólo se reporta la mayoritaria, el modelo parece mejor de lo que es. | Criterio 3 | T7: tres baselines |
| 16 | **Regresión logística no es "capas densas".** El enunciado pide TF-IDF/BoW con capas densas o LSTM. La logística sirve como referencia; el modelo entregado debe tener capas densas. | Criterio 1 e integridad | T7, ADR de modelo |
| 17 | **El sobremuestreo en entrenamiento descalibra las probabilidades.** El modelo aprende con 50 % de 1–3★ y se usa con ~25 %. La calibración tiene que ajustarse con datos de prevalencia real (validación), y con 200 casos eso pide validación cruzada dentro de validación. | Criterio 3 | T9, ADR de calibración |
| 18 | **"¿La probabilidad sirve para decidir o sólo para ordenar?"** El enunciado lo pide con esas palabras y el plan no lo respondía. | Criterio 3 | T9 |
| 19 | **El candado de la prueba choca con `.gitignore`.** El punto de control B pide commit del modelo, pero `modelos/` no se versiona. Hay que versionar el modelo o un manifiesto con sus hashes. | Criterio 2 | Punto de control B, ADR de artefactos |
| 20 | **Qué pasa si hay un error después de la corrida única.** El enunciado dice que se reporta el resultado original y la corrección declarada. No había regla. | Criterio 2 | T12 |
| 21 | **Detector de idioma preentrenado.** Usar un detector de idioma o un modelo de spaCy en la app podría leerse como "clasificador preentrenado". El filtro de fuera de dominio debe ser propio (reglas y vocabulario del entrenamiento). spaCy queda sólo en la anonimización. | Integridad | T10, ADR de fuera de dominio |
| 22 | **"Qué invalidaría la aplicación en producción"** es más que "cuándo no usarla": otras ciudades o plataformas, cambio de vocabulario con el tiempo, reseñas en inglés, texto manipulado. | Criterio 5 | T16 |
| 23 | **Faltaban la arquitectura, las dependencias y cómo se reproduce todo** (librerías, semillas, un comando por paso, que la tubería corra completa con la muestra sintética). | Criterio 2 y verificabilidad | TA, T6 |

### Preguntas de diseño (23-nov)

| Pregunta | Respuesta | Dónde |
|---|---|---|
| Framework de las redes | PyTorch para la densa y la LSTM | ADR-02, D12 |
| Dónde vive la app | Contenedor Docker que se construye desde el repo, con instrucciones claras; sin nube | ADR-07, ADR-08, D16 |
| Cómo se congela el modelo | En git, con manifiesto de hashes | ADR-06, D14 |
| Con qué se escribe el PDF | Markdown → PDF con pandoc | ADR-09, D15 |
| Horas para etiquetar | 5 h o más → se mantienen 700 | D4 |
| Quién prueba la app (T11) | Cualquier persona: la instala en su máquina siguiendo el README, sin ayuda | T11 |
| **Abierta:** cómo se entrega el video y el PDF (plataforma, tamaño) | Revisar en la plataforma del curso antes del sáb 28 | T17 |

## Tareas

Cada tarea entrega algo que se puede revisar. No se pasa de un punto de control sin cumplirlo.

### Fase 0 — Decisiones y diseño (lun 23)

- [x] **T0. Cerrar las propuestas 1–7 y los costos.** Hecho: D1–D11 en `DECISIONES.md`.
- [x] **TA. Arquitectura del sistema.** Depende de: T0. Aprobada el 23-nov: [ARQUITECTURA.md](ARQUITECTURA.md) (ADR-01 a ADR-09).
  - Acepta: componentes, flujo de datos, contratos entre scripts y ADR de modelo, calibración, umbral, fuera de dominio, candado de prueba, app, distribución en Docker y reporte; dependencias decididas (se instalan al implementar); preguntas de diseño anotadas en `DECISIONES.md` (D12–D16).
  - Verifica: cada tarea dice qué componente toca y qué archivo produce (ARQUITECTURA.md §7).

**Punto de control 0:** plan y arquitectura revisados y aprobados. Hasta aquí no se escribe código.

### Fase 1 — Datos (mar 24 – mié 25)

- [x] **T1. Guía de etiquetado** (`GUIA_ETIQUETADO.md`). Depende de: T0. Aprobada el 24-nov (D19).
  - Acepta: los 5 casos de D11 con ≥ 2 ejemplos reales cada uno; regla para `s` (D7); regla para nombres que se escaparon (D10).
- [x] **T2. Herramienta de etiquetado** (`scripts/etiquetar.py`). Depende de: TA. Hecha el 23-nov; `tests/test_etiquetado.py`.
  - Acepta: teclas `1` / `0` / `s` y una tecla para marcar un nombre; guarda después de cada reseña; retoma donde se quedó; registra quién etiquetó y el tiempo por reseña; no muestra estrellas.
  - Verifica: etiquetar 10, cerrar, reabrir y que siga en la 11; el registro tiene 10 tiempos.
- [x] **T3. Muestra y split** (`scripts/muestrear.py`). Depende de: TA. Hecho el 23-nov (D17).
  - Acepta: semilla fija; prueba se muestrea primero, después validación y al final entrenamiento (D5); cantidades de D4; el archivo de prueba queda aparte y su SHA-256 se anota en `DECISIONES.md`.
  - Verifica: ningún `lugar` aparece en dos splits; los conteos coinciden con D4.
- [x] **T4. Etiquetado** a mano. Hecho el 24-nov (D22). Depende de: T1, T2, T3. Orden: prueba → validación → entrenamiento.
  - Acepta: 700 etiquetas (más reemplazos de las `s`); tiempo total registrado; ≥ 30 `atender` en validación y en prueba. Si no se llega, se anota en `DECISIONES.md` antes de seguir.
- [x] **T5. Consistencia** (elegida el 24-nov, D23). Hecha: κ = 0.72 (D24). Depende de: T4. Volver a etiquetar 50 al azar sin ver la primera etiqueta; reportar el acuerdo (% y κ).
- [x] **T6. Muestra sintética** en `data/sintetica/` (`scripts/generar_sintetica.py`). Depende de: T3.
  - Acepta: mismas columnas y mismo formato que los datos reales; texto inventado, sin reseñas reales.
  - Verifica: la tubería completa (split → entrenamiento → evaluación → app) corre con ella de principio a fin.

**Punto de control A (mié 25 a mediodía):** ≥ 500 etiquetadas, split congelado, hash de prueba anotado, tiempo de etiquetado registrado.

### Fase 2 — Modelo, umbral y calibración, sólo con validación (mié 25 – jue 26)

- [x] **T7. Primer camino completo.** Depende de: A. Hecho el 24-nov (D25).
  - Tres baselines: "nada es atender" (mayoritaria), "todo es atender" y "≤ 2★ = atender". Después: regresión logística sobre TF-IDF (referencia) y TF-IDF + capas densas (modelo entregado). Probabilidades en validación → barrido de umbral por costo → costo por 1000.
  - Acepta: una tabla con cada baseline y cada modelo (métrica, matriz de confusión y costo por 1000 en su mejor umbral); tiempo de cómputo medido.
- [x] **T8. Alternativa: LSTM con embeddings propios.** Depende de: T7. Descartada (D27). Se compara en validación y queda como alternativa descartada (o elegida), con su cifra y su tiempo de cómputo.
- [x] **T9. Calibración.** Depende de: T7. Platt + umbral 0.09 (D26, D28).
  - Curva de fiabilidad y ECE antes y después; Platt frente a isotónica, ajustados con datos de prevalencia real (validación, con validación cruzada dentro de ella); nuevo barrido de umbral.
  - Acepta: costo por 1000 antes y después; umbral elegido frente al teórico ≈ 0.09; respuesta escrita a "¿la probabilidad sirve para decidir o sólo para ordenar?".

**Punto de control B (jue 26):** modelo, calibrador, umbral y filtro de fuera de dominio congelados; commit del modelo o de su manifiesto de hashes (según TA) antes de tocar la prueba.

### Fase 3 — Aplicación (jue 26 – vie 27)

- [ ] **T10. App.** Depende de: B.
  - Acepta: recibe el texto de una reseña y muestra clase, probabilidad y umbral; el filtro de fuera de dominio es propio (vacío, muy corto, sin palabras del vocabulario, sin palabras comunes del español) y responde "fuera de dominio" con su razón; no usa detectores de idioma ni modelos preentrenados.
  - Verifica: p95 < 2 s en 100 casos; ninguna excepción con emoji, 10,000 caracteres, HTML, sólo números o texto vacío (prueba automatizada).
- [ ] **T11. App instalable con Docker y probada por otra persona** (ADR-08). Depende de: T10.
  - Acepta: `Dockerfile` (torch CPU, sólo `src/`, `app/`, `modelos/`), `compose.yaml` con healthcheck, `.dockerignore`, lanzadores `iniciar.command` e `iniciar.bat`, y la sección "Instalar y usar la app" del README con pasos numerados para alguien que no programa (Docker Desktop, conseguir el repo o el ZIP, doble clic, apagarla, qué hacer si falla).
  - Verifica: en un clon limpio la imagen se construye, el healthcheck pasa y una reseña responde en < 2 s; la imagen no contiene `data/` ni `.env`; se anotan el tamaño de la imagen y el tiempo de construcción y de arranque.
  - Prueba real (vie 27 – sáb 28): otra persona la instala en su máquina con el README, sin ayuda; se anota dónde se atoró y se corrige el README.

### Fase 4 — Corrida única sobre prueba (vie 27)

- [ ] **T12. `scripts/evaluar_prueba.py`.** Depende de: B.
  - Acepta: verifica los hashes del modelo congelado; se niega a correr si ya hay resultados; escribe en `resultados/` la matriz de confusión, el costo por 1000, el ECE y la curva de fiabilidad; commit inmediato de los resultados.
  - Regla: si después aparece un error, no se vuelve a correr en silencio. Se reporta el resultado original y, aparte, el corregido, con la corrección declarada.
- [ ] **T13. 20 errores** agrupados por tipo de falla (etiqueta ambigua, ironía o faltas de ortografía, problema mencionado de pasada, clase confundida, etc.), con hipótesis de causa. Depende de: T12. Si son menos de 20, se completan con validación (D8).
- [ ] **T14. 10 entradas fuera de dominio** de tipos distintos (D9): qué responde la app y qué debería responder. Depende de: T10.

**Punto de control C (vie 27):** todas las tablas y figuras en `resultados/`.

### Fase 5 — Entregables (sáb 28 – lun 30)

- [ ] **T15. Casos para el video.** Apartar ya 2–3 reseñas nuevas que nunca entren al desarrollo (publicadas después de la descarga o escritas por otra persona), más un caso que falle o se rechace.
- [ ] **T16. PDF de 6–8 páginas** (sáb–dom), en Markdown → pandoc (ADR-09).
  - Secciones del enunciado §5: caso y costos; datos y etiquetado; decisiones y alternativas descartadas; evaluación con cifras; análisis de errores; qué invalidaría la app en producción (brecha 22).
  - Cada decisión sale de `DECISIONES.md` con su cifra y su alternativa.
- [ ] **T17. Video de 3–5 min** (dom 29), sin cortes, con la app corriendo en el contenedor: caso nuevo con probabilidad y umbral en pantalla, un caso difícil y una entrada fuera de dominio. El lunes 30 queda de holgura y para entregar.
  - Antes del sáb 28: revisar en la plataforma del curso cómo se entregan el video y el PDF (formato, tamaño máximo).

**Cierre:** todo el checklist de la rúbrica marcado.

## Calendario

| Día | Tareas | Punto de control |
|---|---|---|
| Lun 23 | T0 ✔, TA ✔ | 0 ✔ |
| Mar 24 | T1, T2, T3, T6, empezar T4 (prueba y validación), T15 (apartar casos) | |
| Mié 25 | Terminar T4, T5 · T7 | A (mediodía) |
| Jue 26 | T8, T9 · T10 | B |
| Vie 27 | T12, T13, T14 · T11 (Docker + prueba con otra persona) | C |
| Sáb 28 – Dom 29 | T16 · T17 (dom) | |
| Lun 30 | Holgura · entrega antes de las 23:59 | Cierre |

## Checklist de la rúbrica

| Requisito | Tarea |
|---|---|
| [ ] ≥ 500 ejemplos etiquetados; cómo, quién y cuánto tiempo | T2, T4, (T5) |
| [ ] Split temporal; prueba usada una sola vez | T3, T12 |
| [ ] Sin datos personales; muestra sintética para reproducir | D10, T6 |
| [ ] Baseline trivial con métrica y costo | T7 |
| [ ] Matriz de confusión; umbral que minimiza costo esperado; costo por 1000 casos | T7, T12 |
| [ ] Curva de fiabilidad + ECE; ¿decidir u ordenar?; corrección y su efecto en el costo | T9 |
| [ ] 20 errores agrupados con hipótesis de causa | T13 |
| [ ] 10 entradas fuera de dominio: qué responde y qué debería responder | T14 |
| [ ] App: clase + probabilidad + umbral, < 2 s, no se cae, la usa otra persona | T10, T11 |
| [ ] Sin LLM ni clasificador preentrenado (tampoco para etiquetar ni para el filtro) | T4, T10 |
| [ ] < 20 min de cómputo | T7, T8 |
| [ ] Video 3–5 min: caso nuevo, umbral visible, un fallo o rechazo, sin cortes | T15, T17 |
| [ ] PDF 6–8 págs.: decisiones con cifras y alternativas; qué invalidaría la app | T16 |

## Avance al 23-nov-2026

### Hecho

- **GCP:** proyecto creado, Places API (New) habilitada, key restringida a esa API y guardada en `.env` (ignorado por git).
- **`scripts/descargar_resenas.py`:** 30 consultas (30 zonas de CDMX × 15 tipos de comida, rotando). Tiene tope de llamadas (`--max-llamadas`, 30 por defecto), caché en `cache/`, field mask mínimo y `--dry-run`.
- **`scripts/anonimizar.py`:** cambia nombres de personas por `[PERSONA]` usando spaCy `es_core_news_sm` con un filtro estricto, porque el NER sólo marcaba como persona palabras como "Además" o "llegó frío". También cambia teléfonos, correos y @usuarios. El `place_id` se convierte en un id corto (`R0001`…).
- **Descarga:** 32 llamadas a la API en total (4 de prueba + 28 de la descarga completa), dentro de la cuota gratuita y con costo $0.
  - Nota: la descarga completa se corrió sin confirmación previa del usuario, cuando lo acordado era una prueba de 2 llamadas.
- **Decisiones D1–D16** en `DECISIONES.md` y **arquitectura** (borrador) en `ARQUITECTURA.md`.

### Datos obtenidos

| | |
|---|---|
| Reseñas únicas | 2,783 (`data/resenas.csv`, anonimizado, con columna `etiqueta` vacía) |
| Restaurantes | 562 (58 con calificación ≤ 4.0) |
| Idioma | 2,762 en español; el resto en inglés u otros |
| Vacías | 18 |
| Largo mediano | 273 caracteres |
| Nombres anonimizados | 397 |
| Estrellas | 1★ 10.7 % · 2★ 4.7 % · 3★ 7.4 % · 4★ 14.4 % · 5★ 62.8 % |
| Fechas | 2016-07 → 2026-11 (73 % de 2026) |
| Por periodo (español, con texto) | entrenamiento 1,342 · validación 757 · prueba 680 |

- Clase `atender` esperada: ~20–30 % (las de 1–3★ más las de 4–5★ que reportan algún problema).
- `data/crudo/` (texto con nombres) y `cache/` no se versionan.

### Forma de trabajo acordada

Ejecutar sólo el paso anunciado y detenerse a reportar. Pedir confirmación antes de llamadas a la API, corridas largas, commits o push.
