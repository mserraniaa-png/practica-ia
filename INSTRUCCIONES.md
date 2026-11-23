# Práctica 1 — Aplicación de visión o de lenguaje, sin modelos de lenguaje

**Individual · Entrega: lunes 30 de noviembre de 2026, 23:59 (hora de la Ciudad de México)**

**Objetivo.** Entregar una aplicación que funcione sobre datos nuevos y que otra persona pueda usar. La entrega es el video donde se ve funcionando y el PDF donde se explica por qué decide lo que decide.

## 1. Elija un dominio (uno solo)

- **Visión (sesiones 02 y 04).** Red convolucional propia entrenada con imágenes de su entorno. Ejemplos viables: clasificar tipos de documento, piezas buenas o defectuosas, señales o letreros, vegetación o cultivos, calidad de una foto de producto. No use MNIST ni un conjunto de juguete: el valor está en sus propios datos.
- **Lenguaje sin modelos de lenguaje (sesiones 02 y 05).** Clasificador de texto entrenado desde cero con bolsa de palabras o TF-IDF, capas densas o embeddings propios con LSTM. Ejemplos viables: queja contra consulta, urgencia de un ticket, mensaje que debe escalarse a humano, spam o fraude en un formulario, riesgo en una reseña. Un LLM o una API de clasificación preentrenada no cuentan como entrega.

## 2. Datos

- Mínimo **500 ejemplos etiquetados**, binario o de tres clases como máximo. Con menos ejemplos el techo de la aplicación es el conjunto de datos, no el modelo, y eso se califica.
- Declare **cómo etiquetó, quién etiquetó y cuánto tiempo tomó**. Si etiquetó una sola persona, dígalo: es un límite del montaje y debe aparecer en el PDF.
- **Split honesto** y, si los datos tienen fecha, split temporal. El conjunto de prueba no se toca hasta la corrida final.
- Sin datos personales ni identificadores. Para reproducir basta una muestra sintética con la misma estructura.

## 3. La aplicación

- Recibe un caso nuevo —un archivo o un texto— y devuelve **la clase, la probabilidad y el umbral aplicado**. Quien la usa no programa ni reentrena nada.
- Responde en **menos de dos segundos por caso** y no se cae con una entrada atípica.
- El criterio es de uso, no de arquitectura de software: si alguien de su trabajo la usa una vez sin que usted esté presente, la aplicación cumple.

## 4. Evaluación y decisión

- **Baseline trivial** (clase mayoritaria o regla tonta) con su métrica y su costo. Sin baseline no hay escala para interpretar el resto.
- **Matriz de confusión y umbral.** Fije el costo de un falso positivo y de un falso negativo, barra el umbral y elija el que minimiza el costo esperado. Reporte el **costo esperado por cada 1000 casos**.
- **Calibración.** Curva de fiabilidad y ECE. Diga si la probabilidad sirve para decidir o sólo para ordenar; si no está calibrada, corríjala y muestre el efecto sobre el costo.
- **Análisis de errores.** Los **20 casos mal clasificados** más informativos, agrupados por tipo de falla (etiqueta ambigua, imagen borrosa u oclusión, texto irónico o con faltas, clase confundida con otra), con la hipótesis de la causa.
- **Fuera de dominio.** **Diez entradas** que no pertenecen a ninguna clase (foto oscura o de otro objeto, texto vacío o en otro idioma): qué responde la aplicación y qué debería responder.

## 5. Entregables (los dos)

- **Video de la demo, de 3 a 5 minutos.** La aplicación resolviendo un caso que no se usó durante el desarrollo, con la probabilidad y el umbral visibles en pantalla, y al menos un caso difícil donde se equivoque o donde rechace la entrada. Sin cortes que oculten el fallo.
- **PDF con el razonamiento, de 6 a 8 páginas.** Caso elegido y costo de cada tipo de error; datos y etiquetado; decisiones tomadas y las alternativas descartadas; evaluación con cifras; análisis de errores; y qué invalidaría la aplicación en producción.

## 6. Reglas duras

- Prohibido usar un LLM o un servicio de clasificación preentrenado como clasificador. Una red preentrenada de visión se admite sólo como comparación, nunca como modelo entregado.
- El modelo final se corre **una sola vez sobre prueba**. Cualquier ajuste posterior invalida ese resultado y se reporta el anterior con la corrección declarada.
- **Menos de 20 minutos de cómputo** en GPU de 8 GB o en CPU.
- El video es la evidencia de que funciona: lo que no se ve funcionando no cuenta, y lo que sólo funciona en su máquina no se puede verificar.

## 7. Rúbrica (total 10 puntos)

| Criterio | Peso | 10 | 8 | 6 | 4 |
|---|---|---|---|---|---|
| 1. Aplicación funcional | 25% | En el video resuelve un caso nuevo con clase, probabilidad y umbral en pantalla, responde en segundos y además maneja un caso fuera de dominio sin caerse. | Resuelve el caso nuevo pero no muestra el umbral, o muestra sólo casos ya vistos. | Funciona sólo con los datos de entrenamiento o requiere que usted intervenga. | No funciona en el video. |
| 2. Datos y honestidad del experimento | 20% | 500 o más ejemplos, etiquetado documentado con su límite, split temporal o estratificado y prueba intocada hasta la corrida final. | Split correcto con decisiones tomadas mirando validación, declarado en el PDF. | Prueba usada para elegir, o menos de 500 ejemplos. | Sin split o con fuga evidente. |
| 3. Evaluación y umbral | 25% | Baseline, matriz de confusión, barrido de umbral por costo, costo esperado por 1000 casos y calibración con corrección aplicada y su efecto medido. | Umbral por costo sin calibración, o calibración sin efecto en el costo. | Umbral elegido por exactitud o F1, con costo calculado después. | Sólo exactitud, sin umbral ni costo. |
| 4. Análisis de errores y fuera de dominio | 15% | 20 casos difíciles agrupados por tipo de falla con hipótesis de causa, y 10 entradas fuera de dominio con la respuesta esperada. | Análisis de errores sin agrupar, o sin la prueba fuera de dominio. | Lista de errores sin categoría. | No analiza errores. |
| 5. Razonamiento escrito | 15% | Cada decisión con su cifra y la alternativa que descartó; límites declarados y criterio explícito de cuándo no usar la aplicación. | Decisiones justificadas sin las alternativas descartadas. | Describe el procedimiento sin justificarlo. | Sin cifras que sostengan el razonamiento. |

**Condiciones de borde.**

- Sin video, el criterio 1 se califica 0.
- Sin PDF, el criterio 5 se califica 0.
- Sin baseline, el criterio 3 no puede exceder 6.
- Con la prueba usada para decidir, el criterio 2 no puede exceder 4.
- Una entrega que usa un LLM o un clasificador preentrenado como modelo final se califica con 0 en el criterio 1 y se revisa integridad.
