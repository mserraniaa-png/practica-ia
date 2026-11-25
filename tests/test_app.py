"""T10 · la app con el modelo congelado real: responde, no se cae y es rápida."""

import time

import numpy as np
import pytest

gr = pytest.importorskip("gradio")
from app.app import EJEMPLOS, PREDICTOR, construir, tarjeta  # noqa: E402

RARAS = ["", "   ", "😋" * 50, "<script>alert(1)</script>", "42 007 99", "x" * 10_000,
         "la comida " * 2000, "Great food", "\x00\x01", "a b c d e f", "[PERSONA] [PERSONA] [PERSONA]"]


@pytest.mark.parametrize("texto", EJEMPLOS + RARAS)
def test_no_se_cae_y_muestra_umbral(texto):
    salida = tarjeta(texto)
    assert "Umbral aplicado" in salida and "<script>" not in salida


def test_ejemplos_de_las_dos_clases_y_fuera_de_dominio():
    clases = {PREDICTOR.predecir(t).clase for t in EJEMPLOS}
    assert clases == {"atender", "no_atender", "fuera_de_dominio"}


def test_latencia_p95_menor_a_200_ms():
    textos = [f"{EJEMPLOS[i % 4]} visita número {i}" for i in range(100)]
    ms = []
    for t in textos:
        t0 = time.perf_counter()
        tarjeta(t)
        ms.append((time.perf_counter() - t0) * 1000)
    assert np.percentile(ms, 95) < 200


def test_construye_la_interfaz():
    assert construir() is not None


def test_entrada_enorme_se_topa_en_el_servidor():
    from app.app import MAX_ENTRADA, contador
    assert f"{MAX_ENTRADA:,} caracteres" in contador("a " * 100_000)
    assert "Umbral aplicado" in tarjeta("la comida " * 100_000)
