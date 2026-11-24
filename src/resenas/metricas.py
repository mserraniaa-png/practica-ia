"""Métricas compartidas. Por ahora: acuerdo entre dos etiquetados (T5)."""

import numpy as np


def acuerdo(a, b) -> float:
    a, b = np.asarray(a), np.asarray(b)
    return float((a == b).mean())


def kappa_cohen(a, b) -> float:
    """κ = (p_o − p_e) / (1 − p_e). Si p_e = 1 (una sola clase en ambos), devuelve 1 si coinciden."""
    a, b = np.asarray(a), np.asarray(b)
    clases = np.union1d(a, b)
    p_o = (a == b).mean()
    p_e = sum((a == c).mean() * (b == c).mean() for c in clases)
    if p_e == 1:
        return 1.0 if p_o == 1 else 0.0
    return float((p_o - p_e) / (1 - p_e))
