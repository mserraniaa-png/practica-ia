"""Nombres que se escaparon a la anonimización automática (D10, D23).

Los nombres viven fuera de git:
  data/nombres_escapados.txt   un nombre por línea (lo lee también auditar_seguridad.py)
  data/nombres_revisados.csv   id, nombres: qué reseña marcada se revisó y qué nombres tenía

Reemplazo:
  - En la reseña donde se marcó: sin distinguir mayúsculas (el nombre puede venir en minúsculas).
  - En las demás: sólo con la grafía exacta, para no tocar palabras comunes
    (p. ej. un nombre "Rosa" no cambia "salsa rosa").
"""

import csv
import re
from pathlib import Path

import pandas as pd

from resenas import config

NOMBRES = config.DATA / "nombres_escapados.txt"
REVISADOS = config.DATA / "nombres_revisados.csv"
MARCA = "[PERSONA]"


def _patron(nombre: str, ignorar_mayusculas: bool) -> re.Pattern:
    return re.compile(rf"(?<!\w){re.escape(nombre)}(?!\w)", re.IGNORECASE if ignorar_mayusculas else 0)


def reemplazar(texto: str, nombres_globales: set, nombres_de_esta: set = frozenset()) -> str:
    # Primero los más largos, para que "Fulano Mengano" se cambie antes que "Fulano".
    for n in sorted(nombres_de_esta, key=len, reverse=True):
        texto = _patron(n, True).sub(MARCA, texto)
    for n in sorted(nombres_globales, key=len, reverse=True):
        texto = _patron(n, False).sub(MARCA, texto)
    return texto


def leer_nombres(ruta: Path = NOMBRES) -> set:
    if not ruta.exists():
        return set()
    return {l.strip() for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()}


def leer_revisados(ruta: Path = REVISADOS) -> dict:
    """id → conjunto de nombres (vacío si se revisó y no había nombre)."""
    if not ruta.exists():
        return {}
    df = pd.read_csv(ruta, dtype=str).fillna("")
    return {i: {n.strip() for n in ns.split("|") if n.strip()} for i, ns in zip(df["id"], df["nombres"])}


def guardar_revision(id_: str, nombres: set, ruta_rev: Path = REVISADOS, ruta_nom: Path = NOMBRES) -> None:
    nuevo = not ruta_rev.exists()
    with ruta_rev.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nuevo:
            w.writerow(["id", "nombres"])
        w.writerow([id_, "|".join(sorted(nombres))])
    todos = leer_nombres(ruta_nom) | nombres
    ruta_nom.write_text("".join(f"{n}\n" for n in sorted(todos)), encoding="utf-8")
