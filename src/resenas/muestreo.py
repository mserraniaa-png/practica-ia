"""Muestra y split (D3, D4, D5, D7).

Orden: prueba → validación → entrenamiento. Cada split excluye los restaurantes
que ya aparecen (incluidas las reservas) en los splits muestreados antes, así que
reponer una ambigua con una reserva nunca rompe la separación por restaurante.

Cada fila de la muestra tiene un `orden` dentro de su split: primero las
principales (`reserva = False`), después las reservas. Quien etiqueta recorre las
principales y, por cada ambigua, toma la siguiente reserva del mismo split y estrato.
"""

import numpy as np
import pandas as pd

from resenas import config
from resenas.datos import aptas, periodo


class PoolInsuficiente(ValueError):
    pass


def _barajar(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    # Se ordena por id antes de barajar: el resultado no depende del orden del CSV.
    df = df.sort_values("id")
    return df.iloc[rng.permutation(len(df))]


def _tomar(pool: pd.DataFrame, n: int, reserva: int, split: str,
           rng: np.random.Generator) -> pd.DataFrame:
    if len(pool) < n + reserva:
        raise PoolInsuficiente(f"{split}: hay {len(pool)} reseñas aptas y se piden {n} + {reserva} de reserva")
    elegidas = _barajar(pool, rng).head(n + reserva)
    return pd.DataFrame({
        "id": elegidas["id"].values,
        "split": split,
        "estrato": "aleatorio",
        "reserva": [False] * n + [True] * reserva,
    })


def muestrear(resenas: pd.DataFrame, semilla: int = config.SEMILLA,
              n_prueba: int = config.N_PRUEBA, n_validacion: int = config.N_VALIDACION,
              n_por_estrato: int = config.N_ENTRENAMIENTO_POR_ESTRATO,
              reserva: int = config.RESERVA) -> pd.DataFrame:
    """Devuelve la muestra completa: id, split, estrato, orden, reserva, semilla."""
    rng = np.random.default_rng(semilla)
    df = aptas(resenas).copy()
    df["periodo"] = periodo(df["fecha"])

    prueba = _tomar(df[df["periodo"] == "prueba"], n_prueba, reserva, "prueba", rng)
    lugares_usados = set(df.loc[df["id"].isin(prueba["id"]), "lugar"])

    pool_val = df[(df["periodo"] == "validacion") & ~df["lugar"].isin(lugares_usados)]
    validacion = _tomar(pool_val, n_validacion, reserva, "validacion", rng)
    lugares_usados |= set(df.loc[df["id"].isin(validacion["id"]), "lugar"])

    pool_ent = df[(df["periodo"] == "entrenamiento") & ~df["lugar"].isin(lugares_usados)]
    bajas = pool_ent["estrellas"] <= config.ESTRELLAS_MAX_BAJAS
    partes = []
    for estrato, pool in (("1-3", pool_ent[bajas]), ("4-5", pool_ent[~bajas])):
        if len(pool) < n_por_estrato:
            raise PoolInsuficiente(f"entrenamiento {estrato}★: hay {len(pool)} y se piden {n_por_estrato}")
        b = _barajar(pool, rng)
        partes.append(pd.DataFrame({
            "id": b["id"].values,
            "split": "entrenamiento",
            "estrato": estrato,
            "reserva": [False] * n_por_estrato + [True] * (len(b) - n_por_estrato),
        }))
    ent = pd.concat(partes)
    # Principales de los dos estratos mezcladas al azar, después las reservas.
    ent = ent.iloc[rng.permutation(len(ent))].sort_values("reserva", kind="stable")

    muestra = pd.concat([prueba, validacion, ent], ignore_index=True)
    muestra["orden"] = muestra.groupby("split").cumcount() + 1
    muestra["semilla"] = semilla
    return muestra[["id", "split", "estrato", "orden", "reserva", "semilla"]]


def verificar(muestra: pd.DataFrame, resenas: pd.DataFrame, n_prueba: int = config.N_PRUEBA,
              n_validacion: int = config.N_VALIDACION,
              n_por_estrato: int = config.N_ENTRENAMIENTO_POR_ESTRATO) -> dict:
    """Revisa las reglas del split; lanza AssertionError si alguna falla. Devuelve conteos."""
    m = muestra.merge(resenas[["id", "lugar", "fecha", "estrellas", "idioma", "texto"]], on="id", how="left")
    assert m["lugar"].notna().all(), "hay ids de la muestra que no están en resenas.csv"
    assert not m["id"].duplicated().any(), "hay ids repetidos en la muestra"
    assert len(aptas(m)) == len(m), "hay reseñas no aptas (otro idioma o vacías) en la muestra"
    assert (periodo(m["fecha"]) == m["split"]).all(), "hay reseñas fuera del periodo de su split"

    splits_por_lugar = m.groupby("lugar")["split"].nunique()
    assert (splits_por_lugar == 1).all(), \
        f"{(splits_por_lugar > 1).sum()} restaurantes aparecen en más de un split"

    principales = m[~m["reserva"]]
    conteo = principales.groupby(["split", "estrato"]).size().to_dict()
    esperado = {("prueba", "aleatorio"): n_prueba, ("validacion", "aleatorio"): n_validacion,
                ("entrenamiento", "1-3"): n_por_estrato, ("entrenamiento", "4-5"): n_por_estrato}
    assert conteo == esperado, f"conteos {conteo} ≠ {esperado}"

    ent = m[m["split"] == "entrenamiento"]
    bajas = ent["estrellas"] <= config.ESTRELLAS_MAX_BAJAS
    assert (bajas == (ent["estrato"] == "1-3")).all(), "estrato de entrenamiento mal asignado"

    for split, g in m.groupby("split"):
        assert sorted(g["orden"]) == list(range(1, len(g) + 1)), f"{split}: orden no es 1..n"
        assert not g.sort_values("orden")["reserva"].diff().lt(0).any(), \
            f"{split}: hay principales después de una reserva"

    return {
        "principales": {f"{s}/{e}": n for (s, e), n in conteo.items()},
        "reservas": m[m["reserva"]].groupby("split").size().to_dict(),
        "restaurantes": m.groupby("split")["lugar"].nunique().to_dict(),
        "bajas_en_principales": principales.assign(b=principales["estrellas"] <= 3)
                                           .groupby("split")["b"].sum().to_dict(),
    }
