# practica-ia

Práctica 1 del curso de Inteligencia Artificial Aplicada (MTIIA, Universidad Anáhuac): clasificador que decide si una reseña de restaurante de la CDMX **reporta un problema que el negocio debe atender**. Es un modelo de lenguaje sin LLM (BoW/TF-IDF y capas densas).

- [INSTRUCCIONES.md](INSTRUCCIONES.md): enunciado y rúbrica.
- [PLAN.md](PLAN.md): caso, datos, calendario y checklist.

Las reseñas descargadas de Google Maps no se versionan; para reproducir hay una muestra sintética (inventada) en `data/sintetica/`:

```bash
uv sync
uv run python scripts/muestrear.py --sintetica   # reproduce la muestra: "sin cambios"
uv run pytest                                    # pruebas, incluida la de punta a punta
```
