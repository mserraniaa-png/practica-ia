"""T9 · métricas de calibración y calibradores."""

import numpy as np
import pytest

from resenas.calibracion import Isotonica, Platt, costo_honesto, fuera_de_parte
from resenas.metricas import brier, curva_fiabilidad, ece


def test_ece_cero_si_la_frecuencia_coincide():
    y = np.array([1, 0, 0, 0] * 5 + [1, 1, 1, 0] * 5)
    p = np.array([0.25] * 20 + [0.75] * 20)
    assert ece(y, p) == pytest.approx(0)


def test_ece_y_brier_a_mano():
    y, p = np.array([1, 1, 0, 0]), np.array([0.95, 0.95, 0.95, 0.95])
    assert ece(y, p) == pytest.approx(0.45)
    assert brier(y, p) == pytest.approx((0.05**2 * 2 + 0.95**2 * 2) / 4)
    assert curva_fiabilidad(y, p) == [{"contenedor": 9, "p_media": 0.95, "observada": 0.5, "n": 4}]


@pytest.fixture
def datos():
    rng = np.random.default_rng(0)
    verdadera = rng.uniform(0, 1, 400)
    y = (rng.uniform(0, 1, 400) < verdadera).astype(int)
    sesgada = verdadera ** 0.3                 # sobreestima: descalibrada pero ordena bien
    return sesgada, y, np.arange(400) // 2


@pytest.mark.parametrize("clase", [Platt, Isotonica])
def test_calibrar_reduce_ece(datos, clase):
    p, y, grupos = datos
    q = fuera_de_parte(p, y, grupos, "platt" if clase is Platt else "isotonica", 0)
    assert ece(y, q) < ece(y, p)


def test_platt_es_monótona(datos):
    p, y, _ = datos
    q = Platt().fit(p, y).transform(np.linspace(0.01, 0.99, 50))
    assert np.all(np.diff(q) >= 0)


def test_costo_honesto_suma_todas(datos):
    p, y, grupos = datos
    c = costo_honesto(p, y, grupos, "platt", "barrido", 0)
    assert c["vp"] + c["fp"] + c["fn"] + c["vn"] == len(y) and len(c["umbrales"]) == 5
