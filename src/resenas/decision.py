"""Costo esperado y umbral (D2, ADR-04)."""

import numpy as np
import pandas as pd

from resenas import config

UMBRALES = np.round(np.arange(0.01, 1.0, 0.01), 2)


def matriz(y, pred) -> dict:
    y, pred = np.asarray(y).astype(int), np.asarray(pred).astype(int)
    return {"vp": int(((y == 1) & (pred == 1)).sum()), "fp": int(((y == 0) & (pred == 1)).sum()),
            "fn": int(((y == 1) & (pred == 0)).sum()), "vn": int(((y == 0) & (pred == 0)).sum())}


def costo_por_1000(y, pred, costo_fp: float = config.COSTO_FP, costo_fn: float = config.COSTO_FN) -> float:
    """Minutos de gerente por cada 1000 reseñas: 1000 × (FP·c_fp + FN·c_fn) / n."""
    m = matriz(y, pred)
    return 1000 * (m["fp"] * costo_fp + m["fn"] * costo_fn) / len(np.asarray(y))


def barrido(y, prob, umbrales=UMBRALES, **costos) -> pd.DataFrame:
    """Para cada umbral: predice atender si prob ≥ umbral; costo por 1000 y matriz."""
    prob = np.asarray(prob)
    filas = []
    for u in umbrales:
        pred = prob >= u
        filas.append({"umbral": float(u), "costo_1000": costo_por_1000(y, pred, **costos), **matriz(y, pred)})
    return pd.DataFrame(filas)


def mejor_umbral(tabla: pd.DataFrame) -> pd.Series:
    """El de menor costo; si hay empate, el más alto (manda menos reseñas al gerente)."""
    minimo = tabla["costo_1000"].min()
    return tabla[np.isclose(tabla["costo_1000"], minimo)].sort_values("umbral").iloc[-1]


def umbral_teorico(costo_fp: float = config.COSTO_FP, costo_fn: float = config.COSTO_FN) -> float:
    """Con probabilidades calibradas: atender si p·c_fn > (1−p)·c_fp → p > c_fp / (c_fp + c_fn)."""
    return costo_fp / (costo_fp + costo_fn)
