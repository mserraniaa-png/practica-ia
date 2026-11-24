"""Un solo lugar para cada número y cada ruta del proyecto."""

import os
from pathlib import Path

# RESENAS_RAIZ permite indicar la raíz (contenedor, Space); por omisión, la del repo.
RAIZ = Path(os.environ.get("RESENAS_RAIZ") or Path(__file__).resolve().parents[2])
DATA = RAIZ / "data"
SINTETICA = DATA / "sintetica"

# Nombres de archivo; el directorio es DATA o SINTETICA según la corrida.
RESENAS = "resenas.csv"
MUESTRA = "muestra.csv"                # entrenamiento y validación
MUESTRA_PRUEBA = "muestra_prueba.csv"  # prueba, aparte (su SHA-256 va en DECISIONES.md)

SEMILLA = 20261123

# D3 · split temporal: [inicio, fin)
CORTE_VALIDACION = "2026-07-01"
CORTE_PRUEBA = "2026-10-01"

# D9 · sólo reseñas en español con texto
IDIOMA = "es"

# D4 · cuántas etiquetar
N_PRUEBA = 200
N_VALIDACION = 200
N_ENTRENAMIENTO_POR_ESTRATO = 150      # 150 de 1–3★ y 150 de 4–5★
ESTRELLAS_MAX_BAJAS = 3                # estrato "bajas" = 1–3★

# D7 · reservas para reponer las ambiguas en prueba y validación.
# En entrenamiento todo el pool restante queda como reserva.
RESERVA = 20

# D2 · costos en minutos de gerente
COSTO_FP = 3
COSTO_FN = 30
