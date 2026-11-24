"""T6 · la tubería corre completa con data/sintetica/ (sólo lectura: no regenera nada)."""

import subprocess
import sys

import pandas as pd

from resenas import config
from resenas.datos import COLUMNAS_RESENAS, cargar_resenas
from resenas.etiquetado import COLUMNAS, cargar_muestra_completa, leer, siguiente
from resenas.muestreo import verificar

S = config.SINTETICA


def correr(*args, entrada=""):
    return subprocess.run([sys.executable, *args], cwd=config.RAIZ, input=entrada,
                          capture_output=True, text=True, check=True).stdout


def test_misma_estructura_que_los_datos_reales():
    df = pd.read_csv(S / config.RESENAS, dtype=str)
    assert list(df.columns) == COLUMNAS_RESENAS + ["etiqueta"]
    assert list(leer(S / "etiquetas.csv").columns) == COLUMNAS


def test_muestra_cumple_el_split():
    verificar(cargar_muestra_completa(S), cargar_resenas(S / config.RESENAS))


def test_muestrear_reproduce_la_muestra():
    salida = correr("scripts/muestrear.py", "--sintetica")
    assert salida.count("sin cambios") == 2


def test_etiquetado_completo():
    assert siguiente(cargar_muestra_completa(S), leer(S / "etiquetas.csv")) is None
    assert "Objetivos de D4 cumplidos" in correr("scripts/etiquetar.py", "--sintetica", entrada="q\n")
