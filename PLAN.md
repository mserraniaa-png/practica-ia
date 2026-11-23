# Plan — Práctica 1: ¿esta reseña de restaurante hay que atenderla?

Enunciado y rúbrica: [INSTRUCCIONES.md](INSTRUCCIONES.md). Entrega: **lunes 30-nov-2026, 23:59 (CDMX)**.

## El caso

Un restaurante (o una cadena) recibe reseñas en Google Maps y nadie alcanza a leerlas todas. La aplicación lee **una reseña** de cualquier restaurante y responde si **reporta un problema que el negocio debe atender**, con su probabilidad y el umbral aplicado.

- **Dominio:** lenguaje sin modelos de lenguaje (BoW / TF-IDF + capas densas; LSTM con embeddings propios como alternativa).
- **Clases (binario):** `atender` (reporta un problema concreto: servicio, higiene, cobro, tiempo, comida en mal estado…) / `no_atender` (elogio, opinión de gusto, comentario neutro).
- **La etiqueta no son las estrellas:** un 4★ con "el baño estaba sucio" es `atender`; un 2★ con "caro pero rico" es `no_atender`. Las estrellas se usan sólo como baseline.
- **Costos (a fijar y justificar en el PDF):**
  - Falso negativo: un problema real queda sin atender → cliente perdido, riesgo sanitario o reputacional.
  - Falso positivo: un gerente lee una reseña que no lo requería → pocos minutos.
  - FN ≫ FP (punto de partida a discutir: FN = 10 × FP).

## Datos

- **Fuente:** Google Places API (New), restaurantes de CDMX. 5 reseñas "más relevantes" por lugar → muchos restaurantes con pocas reseñas cada uno (mejor variedad).
- **Búsquedas:** ~30 consultas por colonia × tipo de cocina; incluir a propósito lugares con calificación ≤ 4.0 para subir la proporción de quejas.
- **Meta:** ~1,000 reseñas descargadas, **600–800 etiquetadas** (mínimo 500).
- **Campos:** `id`, `fecha` (`publishTime`), `estrellas`, `idioma`, `texto` (`originalText`, no la traducción). Sin autor ni foto.
- **Costo:** $0. Free tier de la tarifa Enterprise + Atmosphere (1,000 llamadas/mes) + tope de cuota diaria en GCP (100/día) + tope de llamadas en el script + caché en disco.
- **Etiquetado:** una sola persona (yo), con guía de criterios escrita antes de empezar; registrar tiempo total. Límite declarado en el PDF.
- **Términos de Google:** el CSV no se publica ni se sube al repo (`.gitignore`); se entrega una muestra sintética con la misma estructura.
- **Split:** temporal por `fecha` (train antiguo / validación / prueba más reciente). Prueba intocada hasta la corrida final.
- **Plan B:** reseñas de Steam (`IUserReviewsService/GetAppReviews`, sin key, `languages[0]=latam|spanish`), pregunta "¿reporta un problema técnico?". Ya probado.

## Pasos y calendario

| Día | Paso | Salida |
|---|---|---|
| Lun 23 | Configurar GCP (API, key restringida, cuota 100/día, presupuesto $1) · script de descarga · prueba con 2 búsquedas | `descargar_resenas.py`, `.env` |
| Mar 24 | Descarga completa · guía de etiquetado · empezar a etiquetar | `data/resenas.csv`, `GUIA_ETIQUETADO.md` |
| Mié 25 | Terminar etiquetado · split temporal · baseline (mayoritaria y "≤2★ = atender") · modelos en validación | notebook de modelado |
| Jue 26 | Barrido de umbral por costo · calibración (curva de fiabilidad, ECE, Platt/isotónica) y efecto en costo · app (Gradio/Streamlit) con detector de fuera de dominio | `app.py` |
| Vie 27 | **Corrida única sobre prueba** · 20 errores agrupados por tipo de falla · 10 entradas fuera de dominio | tablas y figuras |
| Sáb 28 – Dom 29 | PDF de 6–8 páginas | `reporte.pdf` |
| Lun 30 | Video de 3–5 min (caso nuevo, probabilidad y umbral en pantalla, un fallo o rechazo sin cortes) · entrega | `video.mp4` |

## Checklist de la rúbrica

- [ ] ≥ 500 ejemplos etiquetados; cómo, quién y cuánto tiempo
- [ ] Split temporal; prueba usada una sola vez
- [ ] Muestra sintética para reproducir
- [ ] Baseline trivial con métrica y costo
- [ ] Matriz de confusión; umbral que minimiza costo esperado; costo por 1000 casos
- [ ] Curva de fiabilidad + ECE; corrección y su efecto en el costo
- [ ] 20 errores agrupados con hipótesis de causa
- [ ] 10 entradas fuera de dominio: qué responde y qué debería responder
- [ ] App: clase + probabilidad + umbral, < 2 s, no se cae con entradas raras
- [ ] < 20 min de cómputo
- [ ] Video 3–5 min sin cortes que oculten fallos
- [ ] PDF 6–8 págs.: decisiones con cifras y alternativas descartadas; cuándo NO usar la app
