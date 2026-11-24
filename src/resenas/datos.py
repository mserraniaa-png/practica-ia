"""Carga y validación de los CSV con contrato fijo (ARQUITECTURA.md §2)."""

from pathlib import Path

import pandas as pd

from resenas import config

COLUMNAS_RESENAS = ["id", "lugar", "consulta", "tipo_lugar", "rating_lugar", "fecha",
                    "estrellas", "idioma", "texto"]
COLUMNAS_MUESTRA = ["id", "split", "estrato", "orden", "reserva", "semilla"]
SPLITS = ("entrenamiento", "validacion", "prueba")


def cargar_resenas(ruta: Path) -> pd.DataFrame:
    """Lee resenas.csv y falla con un mensaje claro si no cumple el contrato."""
    df = pd.read_csv(ruta, dtype=str).fillna("")
    faltan = [c for c in COLUMNAS_RESENAS if c not in df.columns]
    if faltan:
        raise ValueError(f"{ruta}: faltan columnas {faltan}")
    if df["id"].duplicated().any():
        raise ValueError(f"{ruta}: hay ids repetidos")
    df["fecha"] = pd.to_datetime(df["fecha"], format="%Y-%m-%d")
    df["estrellas"] = pd.to_numeric(df["estrellas"]).astype(int)
    return df


def aptas(df: pd.DataFrame) -> pd.DataFrame:
    """D9: sólo reseñas en español con texto se etiquetan o se usan para entrenar."""
    return df[(df["idioma"] == config.IDIOMA) & (df["texto"].str.strip() != "")]


def periodo(fechas: pd.Series) -> pd.Series:
    """D3: asigna a cada fecha el split temporal al que pertenece."""
    val, pru = pd.Timestamp(config.CORTE_VALIDACION), pd.Timestamp(config.CORTE_PRUEBA)
    return pd.Series(
        ["entrenamiento" if f < val else "validacion" if f < pru else "prueba" for f in fechas],
        index=fechas.index,
    )


# Candado de la prueba (ADR-06): sólo evaluar_prueba.py pone esta variable.
PERMISO_PRUEBA = "RESENAS_PERMITIR_PRUEBA"


class PruebaBloqueada(PermissionError):
    pass


def cargar_etiquetadas(carpeta: Path, splits=("entrenamiento", "validacion")) -> pd.DataFrame:
    """Reseñas con etiqueta válida (0/1, la última de cada id) de los splits pedidos.

    Columnas: id, split, estrato, texto, estrellas, fecha, lugar, y (int).
    Pedir "prueba" falla salvo que el proceso tenga RESENAS_PERMITIR_PRUEBA=1.
    """
    import os

    from resenas.etiquetado import cargar_muestra_completa, leer, vigentes

    if "prueba" in splits and os.environ.get(PERMISO_PRUEBA) != "1":
        raise PruebaBloqueada("El split de prueba sólo se carga desde scripts/evaluar_prueba.py (ADR-06).")
    muestra = cargar_muestra_completa(carpeta)
    muestra = muestra[muestra["split"].isin(splits)]
    vig = vigentes(leer(carpeta / "etiquetas.csv"))
    vig = vig[vig["etiqueta"].isin(["0", "1"])]
    resenas = cargar_resenas(carpeta / config.RESENAS).set_index("id")
    df = muestra[muestra["id"].isin(vig.index)].copy()
    df["y"] = vig.loc[df["id"], "etiqueta"].astype(int).values
    for c in ("texto", "estrellas", "fecha", "lugar"):
        df[c] = resenas.loc[df["id"], c].values
    return df[["id", "split", "estrato", "texto", "estrellas", "fecha", "lugar", "y"]].reset_index(drop=True)
