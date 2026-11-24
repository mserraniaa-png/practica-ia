"""Predicción con el modelo congelado (modelos/): lo usan evaluar_prueba.py, la app y T13/T14.

predecir(texto) → Resultado(clase, probabilidad calibrada, umbral, fuera de dominio, razón, ms).
"""

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from resenas import config
from resenas.calibracion import logit
from resenas.fuera_dominio import FiltroFueraDominio
from resenas.modelos import RedDensa

MODELOS = config.RAIZ / "modelos"
CLASES = {1: "atender", 0: "no_atender"}


@dataclass
class Resultado:
    clase: str                 # "atender", "no_atender" o "fuera_de_dominio"
    probabilidad: float | None  # calibrada; None si fuera de dominio
    umbral: float
    fuera_de_dominio: bool
    razon: str
    aviso: str
    ms: float

    def a_dict(self) -> dict:
        return asdict(self)


class Predictor:
    def __init__(self, carpeta: Path = MODELOS):
        self.config = json.loads((carpeta / "config.json").read_text())
        self.modelo = RedDensa.cargar(carpeta)
        cal = json.loads((carpeta / "calibrador.json").read_text())
        self.a, self.b = cal["a"], cal["b"]
        self.filtro = FiltroFueraDominio.de_dict(json.loads((carpeta / "fuera_dominio.json").read_text()))
        self.umbral = float(self.config["umbral"])

    def probabilidades(self, textos) -> np.ndarray:
        """Probabilidad calibrada (Platt sobre el logit de la red), sin filtro. Para evaluar en lote."""
        crudas = self.modelo.predict_proba(list(textos))
        return 1 / (1 + np.exp(-(self.a * logit(crudas) + self.b)))

    def predecir(self, texto) -> Resultado:
        t0 = time.perf_counter()
        try:
            v = self.filtro.evaluar(texto)
            if v.rechazada:
                return Resultado("fuera_de_dominio", None, self.umbral, True, v.razon, v.aviso,
                                 (time.perf_counter() - t0) * 1000)
            p = float(self.probabilidades([texto])[0])
            clase = CLASES[int(p >= self.umbral)]
            return Resultado(clase, p, self.umbral, False, "", v.aviso, (time.perf_counter() - t0) * 1000)
        except Exception as e:  # la app nunca se cae: se reporta como fuera de dominio
            return Resultado("fuera_de_dominio", None, self.umbral, True, f"Error al procesar: {type(e).__name__}",
                             "", (time.perf_counter() - t0) * 1000)
