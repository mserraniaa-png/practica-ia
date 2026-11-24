"""Calibración (ADR-03): Platt e isotónica, ajustadas con datos de prevalencia real (validación).

`fuera_de_parte` da probabilidades calibradas para cada caso con un calibrador que no lo vio.
`costo_honesto` además elige el umbral sin ver la parte que se mide.
"""

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold

from resenas.decision import barrido, matriz, mejor_umbral

EPS = 1e-6


def logit(p):
    p = np.clip(np.asarray(p, dtype=float), EPS, 1 - EPS)
    return np.log(p / (1 - p))


class SinCalibrar:
    nombre = "sin calibrar"

    def fit(self, p, y):
        return self

    def transform(self, p):
        return np.asarray(p, dtype=float)

    def params(self):
        return {}


class Platt:
    """Regresión logística de una variable sobre el logit de la probabilidad."""
    nombre = "Platt"

    def fit(self, p, y):
        self.lr = LogisticRegression(C=1e6, max_iter=1000).fit(logit(p).reshape(-1, 1), y)
        return self

    def transform(self, p):
        return self.lr.predict_proba(logit(p).reshape(-1, 1))[:, 1]

    def params(self):
        return {"a": float(self.lr.coef_[0, 0]), "b": float(self.lr.intercept_[0])}


class Isotonica:
    nombre = "isotónica"

    def fit(self, p, y):
        self.iso = IsotonicRegression(y_min=0, y_max=1, out_of_bounds="clip").fit(p, y)
        return self

    def transform(self, p):
        return self.iso.predict(np.asarray(p, dtype=float))

    def params(self):
        return {"x": self.iso.X_thresholds_.round(4).tolist(), "y": self.iso.y_thresholds_.round(4).tolist()}


METODOS = {"sin_calibrar": SinCalibrar, "platt": Platt, "isotonica": Isotonica}


def _partes(y, grupos, semilla, n=5):
    return StratifiedGroupKFold(n_splits=n, shuffle=True, random_state=semilla).split(np.zeros(len(y)), y, grupos)


def fuera_de_parte(p, y, grupos, metodo: str, semilla: int) -> np.ndarray:
    p, y = np.asarray(p), np.asarray(y)
    out = np.empty(len(p))
    for tr, te in _partes(y, grupos, semilla):
        out[te] = METODOS[metodo]().fit(p[tr], y[tr]).transform(p[te])
    return out


def costo_honesto(p, y, grupos, metodo: str, umbral, semilla: int) -> dict:
    """Calibrador y umbral se eligen con 4/5; el costo se mide en el 1/5 restante.

    umbral: "barrido" (mínimo costo en las 4/5) o un número fijo (p. ej. el teórico).
    Devuelve la matriz sumada sobre las 5 partes y los umbrales elegidos.
    """
    p, y = np.asarray(p), np.asarray(y)
    total = {"vp": 0, "fp": 0, "fn": 0, "vn": 0}
    umbrales = []
    for tr, te in _partes(y, grupos, semilla):
        cal = METODOS[metodo]().fit(p[tr], y[tr])
        if umbral == "barrido":
            u = float(mejor_umbral(barrido(y[tr], cal.transform(p[tr])))["umbral"])
        else:
            u = float(umbral)
        umbrales.append(u)
        for k, v in matriz(y[te], cal.transform(p[te]) >= u).items():
            total[k] += v
    return {**total, "umbrales": umbrales}
