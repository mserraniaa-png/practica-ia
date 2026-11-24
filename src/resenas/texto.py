"""Limpieza de texto compartida por entrenamiento, evaluación y app (ADR-01)."""

import re

MAX_CARACTERES = 5000

_URL = re.compile(r"https?://\S+|www\.\S+")
_NUM = re.compile(r"\d+(?:[.,]\d+)*")
_ESPACIOS = re.compile(r"\s+")


def limpiar(texto) -> str:
    """Minúsculas, URL → <url>, números → <num>, espacios normalizados, recorte a 5,000 caracteres
    (en el último espacio, para no partir una palabra).

    Conserva acentos, signos y emojis: los n-gramas de caracteres los aprovechan.
    """
    if not isinstance(texto, str):
        texto = "" if texto is None else str(texto)
    if len(texto) > MAX_CARACTERES:
        corte = texto[:MAX_CARACTERES]
        texto = corte.rsplit(None, 1)[0] if " " in corte.strip() else corte   # no partir la última palabra
    t = texto.lower()
    t = _URL.sub(" <url> ", t)
    t = _NUM.sub(" <num> ", t)
    return _ESPACIOS.sub(" ", t).strip()
