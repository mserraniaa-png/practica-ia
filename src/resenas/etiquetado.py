"""Lógica del etiquetado (D6, D7, D17): qué reseña sigue, progreso y registro.

`etiquetas.csv` sólo recibe filas nuevas; para cada id vale la última. Una fila con
`ambigua = True` tiene `etiqueta` vacía y hace que se tome una reserva del mismo
split y estrato.
"""

import csv
import os
from pathlib import Path

import pandas as pd

from resenas import config

COLUMNAS = ["id", "etiqueta", "ambigua", "nombre_escapado", "segundos", "etiquetadora",
            "marca_tiempo", "version_guia"]
ORDEN_SPLITS = ("prueba", "validacion", "entrenamiento")
OBJETIVOS = {
    ("prueba", "aleatorio"): config.N_PRUEBA,
    ("validacion", "aleatorio"): config.N_VALIDACION,
    ("entrenamiento", "1-3"): config.N_ENTRENAMIENTO_POR_ESTRATO,
    ("entrenamiento", "4-5"): config.N_ENTRENAMIENTO_POR_ESTRATO,
}


class ReservasAgotadas(RuntimeError):
    pass


def leer(ruta: Path) -> pd.DataFrame:
    if not ruta.exists():
        return pd.DataFrame(columns=COLUMNAS)
    return pd.read_csv(ruta, dtype=str).fillna("")


def vigentes(etiquetas: pd.DataFrame) -> pd.DataFrame:
    """La última fila de cada id, indexada por id."""
    return etiquetas.drop_duplicates("id", keep="last").set_index("id")


def agregar(ruta: Path, fila: dict) -> None:
    """Agrega una fila y la fuerza a disco: un corte de luz pierde a lo más la reseña en pantalla."""
    nuevo = not ruta.exists()
    with ruta.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS)
        if nuevo:
            w.writeheader()
        w.writerow({c: fila.get(c, "") for c in COLUMNAS})
        f.flush()
        os.fsync(f.fileno())


def _validas(ids, vig: pd.DataFrame) -> int:
    e = vig.reindex(list(ids))["etiqueta"]
    return int(e.isin(["0", "1"]).sum())


def siguiente(muestra: pd.DataFrame, etiquetas: pd.DataFrame, objetivos: dict = OBJETIVOS):
    """Devuelve la fila de la muestra que toca etiquetar, o None si ya se cumplieron los objetivos.

    Orden: prueba → validación → entrenamiento; dentro de cada split, por `orden`.
    Una reserva sólo se usa si su estrato no alcanza el objetivo con las válidas más
    las principales que faltan.
    """
    vig = vigentes(etiquetas)
    for split in ORDEN_SPLITS:
        m = muestra[muestra["split"] == split].sort_values("orden")
        faltan = {}
        for estrato, g in m.groupby("estrato"):
            pendientes = (~g["reserva"] & ~g["id"].isin(vig.index)).sum()
            faltan[estrato] = objetivos[(split, estrato)] - _validas(g["id"], vig) - pendientes
        for _, fila in m.iterrows():
            if fila["id"] in vig.index:
                continue
            if not fila["reserva"] or faltan[fila["estrato"]] > 0:
                return fila
        cortos = {e: n for e, n in faltan.items() if n > 0}
        if cortos:
            raise ReservasAgotadas(f"{split}: se acabaron las reservas y faltan {cortos}")
    return None


def progreso(muestra: pd.DataFrame, etiquetas: pd.DataFrame, objetivos: dict = OBJETIVOS) -> dict:
    """Por split: válidas, objetivo, ambiguas, atender y segundos acumulados."""
    vig = vigentes(etiquetas)
    out = {}
    for split in ORDEN_SPLITS:
        ids = muestra.loc[muestra["split"] == split, "id"]
        v = vig.reindex([i for i in ids if i in vig.index])
        filas = etiquetas[etiquetas["id"].isin(ids)]
        out[split] = {
            "validas": int(v["etiqueta"].isin(["0", "1"]).sum()),
            "objetivo": sum(n for (s, _), n in objetivos.items() if s == split),
            "ambiguas": int((v["ambigua"] == "True").sum()),
            "atender": int((v["etiqueta"] == "1").sum()),
            "segundos": float(pd.to_numeric(filas["segundos"], errors="coerce").sum()),
        }
    return out


def cargar_muestra_completa(carpeta: Path) -> pd.DataFrame:
    """Muestra de los tres splits. Leer la de prueba aquí es para etiquetarla, no para evaluar."""
    partes = [pd.read_csv(carpeta / config.MUESTRA), pd.read_csv(carpeta / config.MUESTRA_PRUEBA)]
    m = pd.concat(partes, ignore_index=True)
    m["id"] = m["id"].astype(str)
    m["reserva"] = m["reserva"].astype(str) == "True"
    return m
