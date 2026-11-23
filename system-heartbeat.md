# System heartbeat

Estado vivo del proyecto. Se actualiza **al terminar cada paso** (antes de reportar). Los IDs de tarea y los puntos de control vienen de [PLAN.md](PLAN.md); las decisiones se anotan en [DECISIONES.md](DECISIONES.md), no aquí.

Cómo se actualiza:
1. *Estado actual*: reescribir las líneas que cambiaron.
2. *Tareas* y *Puntos de control*: cambiar el estado y anotar la evidencia (archivo, commit o cifra).
3. *Métricas*: llenar en cuanto exista la cifra.
4. *Bitácora*: agregar una línea arriba (la más reciente primero). No se borran líneas.

Estados: ⬜ pendiente · 🟡 en curso · 🔵 en revisión · ✅ hecho · ⛔ bloqueado · ➖ omitido

## Estado actual

| | |
|---|---|
| Actualizado | lun 23-nov-2026 |
| Faltan para la entrega | 7 días (lun 30-nov, 23:59 CDMX) |
| Fase | 1 — Datos |
| Punto de control | **0** ✅ aprobado · siguiente: **A** (mié 25, mediodía) |
| Último paso | T3 hecho: muestra congelada (semilla 20261123), hashes en D17, 9 pruebas pasan |
| Siguiente paso | T1 (guía de etiquetado) y T2 (`scripts/etiquetar.py`) |
| Bloqueos | Ninguno |
| Sin commit | T3: `src/resenas/`, `scripts/muestrear.py`, `tests/`, `pyproject.toml`, `uv.lock`, docs |

## Puntos de control

| Punto | Fecha meta | Condición | Estado | Evidencia |
|---|---|---|---|---|
| 0 | lun 23 | Plan y arquitectura revisados y aprobados | ✅ | Aprobado por el usuario el 23-nov |
| A | mié 25, mediodía | ≥ 500 etiquetadas, split congelado, hash de prueba anotado, tiempo registrado | ⬜ | |
| B | jue 26 | Modelo, calibrador, umbral y filtro congelados; commit con manifiesto | ⬜ | |
| C | vie 27 | Tablas y figuras de prueba, errores y fuera de dominio en `resultados/` | ⬜ | |
| Cierre | lun 30 | Video y PDF entregados; checklist de la rúbrica completo | ⬜ | |

## Tareas

| ID | Tarea | Día meta | Estado | Evidencia / nota |
|---|---|---|---|---|
| T0 | Decisiones y costos | lun 23 | ✅ | D1–D16 en `DECISIONES.md` |
| TA | Arquitectura | lun 23 | ✅ | `ARQUITECTURA.md` (ADR-01–09) |
| T1 | Guía de etiquetado | mar 24 | ⬜ | |
| T2 | `scripts/etiquetar.py` | mar 24 | ⬜ | |
| T3 | `scripts/muestrear.py` + hash de prueba | mar 24 | ✅ | D17 · `data/muestra.csv`, `data/muestra_prueba.csv` · `tests/test_split.py` |
| T4 | Etiquetado a mano (prueba → validación → entrenamiento) | mar 24 – mié 25 | ⬜ | |
| T5 | Consistencia (opcional) | mié 25 | ⬜ | |
| T6 | Muestra sintética + tubería de punta a punta | mar 24 | ⬜ | |
| T7 | Baselines, logística y red densa en validación | mié 25 | ⬜ | |
| T8 | LSTM (alternativa) | jue 26 | ⬜ | |
| T9 | Calibración | jue 26 | ⬜ | |
| T10 | App Gradio + filtro de fuera de dominio | jue 26 – vie 27 | ⬜ | |
| T11 | Docker + prueba con otra persona | vie 27 – sáb 28 | ⬜ | |
| T12 | Corrida única sobre prueba | vie 27 | ⬜ | |
| T13 | 20 errores agrupados | vie 27 | ⬜ | |
| T14 | 10 entradas fuera de dominio | vie 27 | ⬜ | |
| T15 | Casos nuevos para el video | mar 24 | ⬜ | Apartarlos antes de que entren al desarrollo |
| T16 | PDF (6–8 págs.) | sáb 28 – dom 29 | ⬜ | |
| T17 | Video (3–5 min) | dom 29 | ⬜ | Revisar cómo se entrega antes del sáb 28 |

## Métricas

| Métrica | Valor | Fuente |
|---|---|---|
| Reseñas descargadas | 2,783 de 562 restaurantes | `data/resenas.csv` |
| Llamadas a Places API / costo | 32 / $0 | Avance en `PLAN.md` |
| Etiquetadas (prueba / validación / entrenamiento) | 0 / 0 / 0 de 200 / 200 / 300 | `data/etiquetas.csv` |
| Muestra: 1–3★ en prueba / validación | 53 / 59 de 200 | D17 |
| Reservas (prueba / validación / ent. 1–3★ / ent. 4–5★) | 20 / 20 / 27 / 406 | D17 |
| `atender` (prueba / validación) | — / — (meta ≥ 30 cada uno) | |
| Ambiguas (`s`) | — | |
| Tiempo de etiquetado | — | |
| Nombres escapados a la anonimización | — | |
| Cómputo acumulado | — de 20 min | `resultados/tiempos.json` |
| Costo por 1000 en validación (mejor baseline / modelo) | — / — | |
| ECE antes / después de calibrar | — / — | |
| Umbral elegido (teórico ≈ 0.09) | — | |
| Costo por 1000 en prueba | — | `resultados/prueba/` |
| Latencia p95 de la app | — (meta < 2 s) | |

## Preguntas abiertas

- Cómo se entregan el video y el PDF en la plataforma del curso (formato, tamaño máximo). Antes del sáb 28.
- Quién va a probar la app instalada (T11).

## Bitácora

- **23-nov** · T3: paquete `src/resenas/` (`config`, `datos`, `muestreo`), `scripts/muestrear.py` y `tests/test_split.py` (9 ✔). Muestra congelada; hashes en D17. Las cifras por periodo de D3 se corrigieron a 1,323 / 750 / 689.
- **23-nov** · Punto de control 0 aprobado. Commit de `PLAN.md`, `ARQUITECTURA.md`, `DECISIONES.md`, `CLAUDE.md` y este archivo.
- **23-nov** · Creado `system-heartbeat.md` para seguir el avance.
- **23-nov** · Creado `CLAUDE.md`.
- **23-nov** · `ARQUITECTURA.md` (borrador) y `DECISIONES.md` D12–D16; segunda revisión del plan.
- **23-nov** · Descarga (28 llamadas) y anonimización: 2,783 reseñas, 397 nombres reemplazados. Commit `26c969c`.
- **23-nov** · Enunciado, plan y estructura del repo. Commit `e35f2f9`.
