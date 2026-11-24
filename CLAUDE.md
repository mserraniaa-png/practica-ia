# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Qué es

Práctica 1 del curso de IA Aplicada (MTIIA): clasificador binario que decide si una reseña de restaurante de la CDMX (Google Maps) **reporta un problema que el negocio debe atender** (`atender` / `no_atender`). Dominio "lenguaje sin modelos de lenguaje": TF-IDF + capas densas en PyTorch (modelo entregado), LSTM con embeddings propios como alternativa. Entrega: lun 30-nov-2026, 23:59 CDMX. Todo el proyecto (código, docs, mensajes) está en español.

Documentos fuente, en orden de autoridad:
- `INSTRUCCIONES.md`: enunciado y rúbrica (no se modifica).
- `DECISIONES.md`: registro D1…Dn con cifra y alternativa descartada. Es la fuente del PDF. **Sólo se agregan entradas**; si una decisión cambia, se agrega otra que la reemplaza.
- `ARQUITECTURA.md`: diseño (ADR-01…ADR-09), contratos de datos entre scripts y qué tarea toca qué componente.
- `PLAN.md`: tareas T0–T17, puntos de control (0, A, B, C), calendario y la sección "Avance".
- `system-heartbeat.md`: estado vivo (fase, último y siguiente paso, estado de cada tarea, métricas, bitácora). **Leerlo al empezar y actualizarlo al terminar cada paso**, antes de reportar.

## Estado actual

Punto de control 0 aprobado (23-nov). El avance por tarea está en `system-heartbeat.md`; lo que no aparece ahí como hecho está diseñado en `ARQUITECTURA.md` pero no implementado.

## Comandos

Entorno con `uv` (Python 3.12, `package = false`):

```bash
uv sync
uv run python scripts/descargar_resenas.py --dry-run   # lista consultas, 0 llamadas a la API
uv run python scripts/anonimizar.py                    # data/crudo/resenas_crudas.csv → data/resenas.csv
uv run python scripts/muestrear.py                     # split congelado; no sobrescribe sin --forzar
uv run python scripts/etiquetar.py --etiquetadora <nombre>   # interactivo: lo corre la persona, no Claude
uv run python scripts/etiquetar.py --repaso            # T5, interactivo (persona)
uv run python scripts/revisar_nombres.py               # nombres escapados, interactivo (persona; incluye prueba)
uv run python scripts/consistencia.py                  # T5: acuerdo y κ → resultados/etiquetado/
uv run python scripts/auditar_seguridad.py --historial # antes de cada commit
uv run python scripts/entrenar.py [--sintetica]        # T7/T8: baselines, logística, densa y LSTM en validación (~70 s)
uv run python scripts/calibrar.py [--sintetica]        # T9: calibración y costo honesto
uv run python scripts/congelar.py [--sintetica]        # punto B: modelos/ + MANIFIESTO (no sobrescribe sin --forzar)
uv run python scripts/evaluar_prueba.py                # T12: YA SE CORRIÓ (D29); el candado impide repetirla
uv run python scripts/analizar_errores.py              # T13 → resultados/prueba/errores.md
uv run python scripts/probar_fuera_dominio.py          # T14 → resultados/fuera_dominio/
uv run python app/app.py                               # T10: app Gradio en :7860
uv run pytest                                          # todas las pruebas
uv run pytest tests/test_split.py::test_conteos_y_reservas   # una sola
```

El proyecto es un paquete (`src/resenas`, con hatchling): los scripts y las pruebas hacen `from resenas import config` sin tocar `sys.path`. Si la shell trae un `VIRTUAL_ENV` de otro proyecto, uv lo ignora y avisa; no afecta.

Las dependencias nuevas (scikit-learn, torch CPU, gradio, matplotlib, pytest) se agregan a `pyproject.toml` sólo al implementar la tarea que las necesita. Con el índice CPU de PyTorch, para que la imagen Docker no baje CUDA.

## Arquitectura (planeada; ver ARQUITECTURA.md)

- **Tubería de scripts** que se pasan archivos CSV con contrato fijo (`data/resenas.csv` → `data/muestra.csv` → `data/etiquetas.csv` → `modelos/` → `resultados/`), más un **paquete compartido `src/resenas/`**. Entrenamiento, evaluación y app deben usar el mismo `texto.py`, `predictor.py`, `calibracion.py` y `fuera_dominio.py`: lo que corre la app es exactamente lo que se evaluó. Todas las constantes (rutas, semilla, fechas de corte, costos) van en `config.py`. Sin notebooks como fuente de resultados.
- Cada script lleva `--help` y `--sintetica`; la tubería completa debe correr con `data/sintetica/`.
- `data/etiquetas.csv` sólo recibe filas nuevas (vale la última por `id`).
- App: Gradio en `0.0.0.0:7860`, distribuida como contenedor Docker que se construye desde el repo (ADR-08).

## Reglas duras (romperlas invalida la entrega)

- **Ningún LLM ni modelo preentrenado** como clasificador, para proponer etiquetas (Claude no etiqueta ni sugiere la etiqueta de reseñas de la muestra; los ejemplos de la guía salen de fuera de la muestra, D18), ni en el filtro de fuera de dominio (nada de detectores de idioma). spaCy `es_core_news_sm` se usa **sólo** en `anonimizar.py`.
- **La prueba se toca una sola vez**, con `evaluar_prueba.py`, después de congelar el modelo (hashes en `modelos/MANIFIESTO.sha256`, en git; protocolo en D28). `cargar_etiquetadas` bloquea "prueba" salvo con `RESENAS_PERMITIR_PRUEBA=1`. No modificar `modelos/` ni el código que usa el predictor sin anotarlo en `DECISIONES.md`. No leer, inspeccionar ni usar `split == "prueba"` para ninguna decisión. Umbral, calibración e hiperparámetros salen de validación (o de CV dentro de entrenamiento).
- Split temporal (entrenamiento < 1-jul-2026, validación jul–sep, prueba ≥ 1-oct) y ningún `lugar` en dos splits (D3, D5).
- El umbral se elige por **costo esperado** (FP = 3 min, FN = 30 min, reportado por cada 1000 reseñas), nunca por exactitud ni F1. Hay tres baselines: nada es atender, todo es atender y ≤ 2★.
- La app recibe sólo el texto; las estrellas no son la etiqueta y sólo se usan en un baseline.
- `data/` (salvo `data/sintetica/`), `cache/` y `.env` no se versionan ni entran a la imagen Docker (términos de Google y privacidad). `data/crudo/` contiene nombres sin anonimizar.
- Cómputo total < 20 min en CPU.

## Forma de trabajo acordada

Ejecutar sólo el paso anunciado y detenerse a reportar. **Antes de cada commit** correr `uv run python scripts/auditar_seguridad.py --historial` y no hacer commit si hay hallazgos (pedido del usuario, 24-nov): no se suben la key, texto de reseñas reales ni nombres. Nunca escribir en archivos versionados un nombre que se escapó a la anonimización; van en `data/nombres_escapados.txt` (ignorado). Pedir confirmación antes de llamadas a la Google Places API (cuestan cuota; hay tope `--max-llamadas` y caché en `cache/`), de corridas largas y de push. Desde el 24-nov los commits son **sólo locales**: se hacen después de la auditoría, sin push hasta que el usuario lo pida. Cada decisión nueva se anota en `DECISIONES.md` con su cifra y la alternativa descartada.
