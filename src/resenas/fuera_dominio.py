"""Filtro propio de entradas fuera de dominio (ADR-05). Sin detectores de idioma ni modelos preentrenados.

Reglas en orden; la primera que se cumple rechaza y da su razón:
  1. Vacía: no queda texto después de limpiar.
  2. Muy corta: menos de 3 palabras.
  3. No parece español: fracción de palabras en una lista propia de palabras comunes
     (sacada de las reseñas del periodo de entrenamiento) menor que el umbral X.
  4. Vocabulario desconocido: fracción de palabras en el vocabulario del TF-IDF menor que Y.
  Larga (> 5,000 caracteres): no rechaza; se recorta y se avisa.
X e Y = percentil 1 de esas fracciones en las reseñas del periodo de entrenamiento.
"""

import re
from collections import Counter
from dataclasses import dataclass

import numpy as np

from resenas.texto import MAX_CARACTERES, limpiar

_PALABRA = re.compile(r"[^\W\d_]+")
MIN_PALABRAS = 3
N_COMUNES = 300
PERCENTIL = 1


def palabras(texto) -> list:
    return _PALABRA.findall(limpiar(texto))


@dataclass
class Veredicto:
    rechazada: bool
    razon: str = ""
    aviso: str = ""


class FiltroFueraDominio:
    def ajustar(self, textos_entrenamiento, vocabulario) -> "FiltroFueraDominio":
        docs = [set(palabras(t)) for t in textos_entrenamiento]
        frec = Counter(w for d in docs for w in d)
        self.comunes = sorted(w for w, _ in frec.most_common(N_COMUNES))
        self.vocabulario = sorted(set(vocabulario))
        fr_c, fr_v = [], []
        for t in textos_entrenamiento:
            ws = palabras(t)
            if len(ws) >= MIN_PALABRAS:
                fr_c.append(self._fraccion(ws, set(self.comunes)))
                fr_v.append(self._fraccion(ws, set(self.vocabulario)))
        self.umbral_comunes = float(np.percentile(fr_c, PERCENTIL))
        self.umbral_vocabulario = float(np.percentile(fr_v, PERCENTIL))
        self._preparar()
        return self

    def _preparar(self):
        self._comunes, self._vocab = set(self.comunes), set(self.vocabulario)

    @staticmethod
    def _fraccion(ws, conjunto) -> float:
        return sum(w in conjunto for w in ws) / len(ws) if ws else 0.0

    def evaluar(self, texto) -> Veredicto:
        texto = "" if texto is None else str(texto)
        aviso = f"Texto de {len(texto):,} caracteres: se analizaron los primeros {MAX_CARACTERES:,}." \
            if len(texto) > MAX_CARACTERES else ""
        if not limpiar(texto):
            return Veredicto(True, "Vacía: no hay texto que analizar.", aviso)
        ws = palabras(texto)
        if len(ws) < MIN_PALABRAS:
            return Veredicto(True, f"Muy corta: tiene {len(ws)} palabra(s); se necesitan al menos {MIN_PALABRAS}.", aviso)
        fc = self._fraccion(ws, self._comunes)
        if fc < self.umbral_comunes:
            return Veredicto(True, f"No parece una reseña en español: sólo {fc:.0%} de sus palabras son palabras comunes"
                                   f" de las reseñas (mínimo {self.umbral_comunes:.0%}).", aviso)
        fv = self._fraccion(ws, self._vocab)
        if fv < self.umbral_vocabulario:
            return Veredicto(True, f"Vocabulario desconocido: sólo {fv:.0%} de sus palabras las conoce el modelo"
                                   f" (mínimo {self.umbral_vocabulario:.0%}).", aviso)
        return Veredicto(False, "", aviso)

    def a_dict(self) -> dict:
        return {"comunes": self.comunes, "vocabulario": self.vocabulario, "umbral_comunes": self.umbral_comunes,
                "umbral_vocabulario": self.umbral_vocabulario, "min_palabras": MIN_PALABRAS, "percentil": PERCENTIL}

    @classmethod
    def de_dict(cls, d) -> "FiltroFueraDominio":
        f = cls()
        f.comunes, f.vocabulario = d["comunes"], d["vocabulario"]
        f.umbral_comunes, f.umbral_vocabulario = d["umbral_comunes"], d["umbral_vocabulario"]
        f._preparar()
        return f
