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
| Actualizado | mar 24-nov-2026 |
| Faltan para la entrega | 6 días (lun 30-nov, 23:59 CDMX) |
| Fase | 3–4 — Aplicación y corrida única sobre prueba |
| Punto de control | **B** ✅ (D28) · siguiente: **C** (vie 27) |
| Último paso | Punto B: `modelos/` congelado con manifiesto (D28) |
| Siguiente paso | T12 `evaluar_prueba.py` (corrida única, con confirmación del usuario) · T10 app |
| Bloqueos | Ninguno |
| Sin commit | — |

## Puntos de control

| Punto | Fecha meta | Condición | Estado | Evidencia |
|---|---|---|---|---|
| 0 | lun 23 | Plan y arquitectura revisados y aprobados | ✅ | Aprobado por el usuario el 23-nov |
| A | mié 25, mediodía | ≥ 500 etiquetadas, split congelado, hash de prueba anotado, tiempo registrado | ✅ | D22 (24-nov), un día antes; alerta: velocidad de etiquetado |
| B | jue 26 | Modelo, calibrador, umbral y filtro congelados; commit con manifiesto | ✅ | D28 (24-nov), dos días antes; `modelos/MANIFIESTO.sha256` |
| C | vie 27 | Tablas y figuras de prueba, errores y fuera de dominio en `resultados/` | ⬜ | |
| Cierre | lun 30 | Video y PDF entregados; checklist de la rúbrica completo | ⬜ | |

## Tareas

| ID | Tarea | Día meta | Estado | Evidencia / nota |
|---|---|---|---|---|
| T0 | Decisiones y costos | lun 23 | ✅ | D1–D16 en `DECISIONES.md` |
| TA | Arquitectura | lun 23 | ✅ | `ARQUITECTURA.md` (ADR-01–09) |
| T1 | Guía de etiquetado | mar 24 | ✅ | `GUIA_ETIQUETADO.md` v1, aprobada (D19) |
| T2 | `scripts/etiquetar.py` | mar 24 | ✅ | `tests/test_etiquetado.py` (11 ✔), incluye retomar en la 11 tras 10 |
| T3 | `scripts/muestrear.py` + hash de prueba | mar 24 | ✅ | D17 · `data/muestra.csv`, `data/muestra_prueba.csv` · `tests/test_split.py` |
| T4 | Etiquetado a mano (prueba → validación → entrenamiento) | mar 24 – mié 25 | ✅ | 700 válidas, 12 ambiguas, 1.19 h (D22) |
| T5 | Consistencia | mié 25 | ✅ | Acuerdo 90 %, κ 0.72 [0.45, 0.94] (D24) · `resultados/etiquetado/consistencia.json` |
| T6 | Muestra sintética + tubería de punta a punta | mar 24 | ✅ | D20 · `data/sintetica/` · `tests/test_punta_a_punta.py` |
| T7 | Baselines, logística y red densa en validación | mié 25 | ✅ | D25 · `resultados/validacion/` · densa 675 vs todo-es-atender 2,235 min/1000 |
| T8 | LSTM (alternativa) | jue 26 | ✅ | Descartada: AUC val 0.851, costo honesto ~1,300 (D27) |
| T9 | Calibración | jue 26 | ✅ | Platt + umbral 0.0909, elegido por el usuario (D26, D28) |
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
| Etiquetadas (prueba / validación / entrenamiento) | 200 / 200 / 300 de 200 / 200 / 300 | `data/etiquetas.csv` (hash en D22) |
| Muestra: 1–3★ en prueba / validación | 53 / 59 de 200 | D17 |
| Reservas (prueba / validación / ent. 1–3★ / ent. 4–5★) | 20 / 20 / 27 / 406 | D17 |
| `atender` (prueba / validación) | 42 / 51 (meta ≥ 30 cada uno) ✔ | D22 |
| Ambiguas (`s`) | 12 (4 / 1 / 7) | D22 |
| Consistencia (repaso de 50) | 90 % · κ 0.72, IC 95 % [0.45, 0.94] | D24 |
| Tiempo de etiquetado | 1.19 h · mediana 4.3 s/reseña · 48 % a > 60 car/s | D22 |
| Nombres escapados a la anonimización | 14 marcados, 14 con nombre; 23 nombres en la lista manual; 0 restantes | D22, D24 |
| Cómputo acumulado | 1.3 min (T7+T8 70 s, T9 8 s) de 20 min | `resultados/tiempos.json` |
| Costo por 1000 en validación (mejor baseline / modelo) | 2,235 / honesto 810–960 densa (518–575 logística) | D25, D26 |
| ECE antes / después de calibrar (densa) | 0.099 / 0.059 Platt | D26 |
| Umbral elegido (teórico ≈ 0.09) | 0.0909 teórico, sobre probabilidad calibrada con Platt | D28 |
| Costo por 1000 en prueba | — | `resultados/prueba/` |
| Latencia p95 del predictor (modelo cargado) | 1.6 ms (meta < 2 s) | D28 |

## Preguntas abiertas

- Cómo se entregan el video y el PDF en la plataforma del curso (formato, tamaño máximo). Antes del sáb 28.
- Quién va a probar la app instalada (T11).

## Bitácora

- **24-nov** · Punto B: modelo congelado (densa + Platt + 0.0909) y filtro de fuera de dominio; protocolo de prueba fijado (D28). La auditoría encontró que el vectorizador guardaba n-gramas en orden de texto y `stop_words_`; se corrigió sin cambiar el modelo. 71 pruebas pasan.
- **24-nov** · T9: costo honesto densa 810 (sin calibrar, 0.09) / 833 (Platt, 0.09); ECE 0.099 → 0.059 con Platt; el umbral teórico gana al barrido. T8: LSTM descartada (AUC 0.851). 54 pruebas pasan (D26, D27).
- **24-nov** · T7: scikit-learn, torch (CPU) y matplotlib en `.venv`. Densa AUC val 0.928, costo 675/1000 (umbral 0.13) contra 2,235 del mejor baseline; logística 540. 47 pruebas pasan (D25).
- **24-nov** · Usuario revisó los 14 nombres y repasó 50. Nombres: 0 restantes, 431 `[PERSONA]`, nuevo hash de `resenas.csv` (D24). T5: κ 0.72 ≥ 0.6 → no se re-etiqueta.
- **24-nov** · Usuario eligió T5 (opción A). Hechos `revisar_nombres.py` + segunda pasada de `anonimizar.py` (`privacidad.py`) y `etiquetar.py --repaso` + `consistencia.py` (κ). 32 pruebas pasan (D23).
- **24-nov** · T4 terminado por el usuario: 700 válidas (D22). Punto A cumplido un día antes, con alerta de velocidad (mediana 4.3 s por reseña). Commits sólo locales por ahora.
- **24-nov** · T6: `generar_sintetica.py` (2,783 reseñas inventadas, 1,092 lugares, 700 etiquetas simuladas); `muestrear`/`etiquetar --sintetica` corren; 24 pruebas pasan. `auditar_seguridad.py` en el repo (D21).
- **24-nov** · Auditoría de seguridad antes del commit (contenido nuevo + todo el historial): sin key, sin nombres, sin correos ni teléfonos reales. 4 paráfrasis de la guía compartían ≥ 40 caracteres con la reseña original; se reescribieron. Commit de T1/T2/D19.
- **24-nov** · Guía aprobada por la etiquetadora: R1–R4 sin cambios, R5 = opción A (D19).
- **23-nov** · T1 borrador `GUIA_ETIQUETADO.md` v1 (ejemplos fuera de la muestra, D18) · T2 `scripts/etiquetar.py` + `src/resenas/etiquetado.py`; 20 pruebas pasan. Commit de T3: `c38657e`.
- **23-nov** · T3: paquete `src/resenas/` (`config`, `datos`, `muestreo`), `scripts/muestrear.py` y `tests/test_split.py` (9 ✔). Muestra congelada; hashes en D17. Las cifras por periodo de D3 se corrigieron a 1,323 / 750 / 689.
- **23-nov** · Punto de control 0 aprobado. Commit de `PLAN.md`, `ARQUITECTURA.md`, `DECISIONES.md`, `CLAUDE.md` y este archivo.
- **23-nov** · Creado `system-heartbeat.md` para seguir el avance.
- **23-nov** · Creado `CLAUDE.md`.
- **23-nov** · `ARQUITECTURA.md` (borrador) y `DECISIONES.md` D12–D16; segunda revisión del plan.
- **23-nov** · Descarga (28 llamadas) y anonimización: 2,783 reseñas, 397 nombres reemplazados. Commit `26c969c`.
- **23-nov** · Enunciado, plan y estructura del repo. Commit `e35f2f9`.
