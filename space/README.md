---
title: ¿Hay que atender esta reseña?
emoji: 🍽️
colorFrom: red
colorTo: green
sdk: docker
app_port: 7860
pinned: false
short_description: ¿La reseña de un restaurante reporta un problema?
---

# ¿Hay que atender esta reseña?

Pega el texto de una reseña de restaurante en español. La app dice si **reporta un problema que el negocio debe atender**, con la probabilidad calibrada y el umbral aplicado (3/33 ≈ 9.1 %: dejar pasar una queja cuesta 10 veces más que leer una reseña de más).

- Modelo: TF-IDF (palabras y caracteres) + red densa entrenada desde cero, calibrada con Platt. Sin LLM ni modelos preentrenados.
- Entradas que no son reseñas de restaurante en español se marcan como **fuera de dominio**.
- Sólo sirve para reseñas de restaurantes en español. Una queja de otro tipo de negocio escrita en español se clasifica como si fuera de restaurante.
- No escribas datos personales. El texto se procesa en el servidor y no se guarda.

Práctica 1 del curso de Inteligencia Artificial Aplicada (MTIIA).
