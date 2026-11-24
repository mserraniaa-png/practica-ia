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


def curva_fiabilidad(y, p, contenedores: int = 10):
    """Por contenedor de igual ancho en [0, 1]: probabilidad media, frecuencia observada y n."""
    y, p = np.asarray(y, dtype=float), np.asarray(p, dtype=float)
    idx = np.minimum((p * contenedores).astype(int), contenedores - 1)
    filas = []
    for b in range(contenedores):
        m = idx == b
        if m.any():
            filas.append({"contenedor": b, "p_media": float(p[m].mean()), "observada": float(y[m].mean()), "n": int(m.sum())})
    return filas


def ece(y, p, contenedores: int = 10) -> float:
    """Error de calibración esperado: Σ (n_b / n) · |observada_b − p_media_b|."""
    n = len(np.asarray(y))
    return float(sum(f["n"] / n * abs(f["observada"] - f["p_media"]) for f in curva_fiabilidad(y, p, contenedores)))


def brier(y, p) -> float:
    y, p = np.asarray(y, dtype=float), np.asarray(p, dtype=float)
    return float(((p - y) ** 2).mean())


def bootstrap(fn, y, p, n: int = 2000, semilla: int = 0):
    """IC 95 % por bootstrap de una métrica fn(y, p)."""
    y, p = np.asarray(y), np.asarray(p)
    rng = np.random.default_rng(semilla)
    vals = [fn(y[i], p[i]) for i in (rng.integers(0, len(y), len(y)) for _ in range(n))]
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]
