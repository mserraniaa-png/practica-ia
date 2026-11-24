"""T7 · costo, umbral, limpieza, candado de prueba y modelos."""

import numpy as np
import pytest

from resenas import config
from resenas.datos import PERMISO_PRUEBA, PruebaBloqueada, cargar_etiquetadas
from resenas.decision import barrido, costo_por_1000, matriz, mejor_umbral, umbral_teorico
from resenas.modelos import Logistica, RedDensa
from resenas.texto import limpiar


def test_costo_por_1000_calculado_a_mano():
    y = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
    pred = [1, 0, 1, 1, 0, 0, 0, 0, 0, 0]        # 1 FN, 2 FP → (2·3 + 1·30)/10 · 1000
    assert matriz(y, pred) == {"vp": 1, "fp": 2, "fn": 1, "vn": 6}
    assert costo_por_1000(y, pred) == pytest.approx(3600)


def test_baselines_triviales():
    y = np.array([1] * 25 + [0] * 75)
    assert costo_por_1000(y, np.zeros(100)) == pytest.approx(7500)
    assert costo_por_1000(y, np.ones(100)) == pytest.approx(2250)


def test_barrido_elige_el_mínimo_y_en_empate_el_más_alto():
    y = np.array([1, 1, 0, 0])
    prob = np.array([0.8, 0.6, 0.3, 0.1])
    mejor = mejor_umbral(barrido(y, prob))
    assert mejor["costo_1000"] == 0
    assert mejor["umbral"] == pytest.approx(0.60)     # 0.31…0.60 dan costo 0; gana el más alto


def test_umbral_teorico():
    assert umbral_teorico() == pytest.approx(3 / 33)


@pytest.mark.parametrize("entrada", ["", None, 12345, "😋😋", "<b>hola</b>", "x" * 20000])
def test_limpiar_no_falla(entrada):
    assert isinstance(limpiar(entrada), str) and len(limpiar(entrada)) <= 5000


def test_limpiar_normaliza():
    assert limpiar("Cobraron $295 en https://x.com  ÉL") == "cobraron $ <num> en <url> él"


def test_prueba_bloqueada(monkeypatch):
    monkeypatch.delenv(PERMISO_PRUEBA, raising=False)
    with pytest.raises(PruebaBloqueada):
        cargar_etiquetadas(config.SINTETICA, splits=("prueba",))


def test_carga_entrenamiento_y_validación_sintéticos():
    df = cargar_etiquetadas(config.SINTETICA)
    assert set(df["split"]) == {"entrenamiento", "validacion"} and len(df) == 500
    assert set(df["y"]) <= {0, 1}


@pytest.mark.parametrize("clase", [Logistica, RedDensa])
def test_modelo_reproducible_y_en_rango(clase):
    textos = ["la sopa llegó fría", "muy rico todo", "el mesero fue grosero", "excelente servicio"] * 10
    y = [1, 0, 1, 0] * 10
    kw = {"epocas": 5} if clase is RedDensa else {}
    p1 = clase(**kw).fit(textos, y).predict_proba(["sopa fría", "", "😋"])
    p2 = clase(**kw).fit(textos, y).predict_proba(["sopa fría", "", "😋"])
    assert np.allclose(p1, p2) and ((p1 >= 0) & (p1 <= 1)).all()


def test_lstm_reproducible_y_en_rango():
    from resenas.modelos import LSTMPropia
    textos = ["la sopa llegó fría", "muy rico todo", "el mesero fue grosero", "excelente servicio"] * 10
    y = [1, 0, 1, 0] * 10
    p1 = LSTMPropia(epocas=3).fit(textos, y).predict_proba(["sopa fría", "", "😋", "x" * 6000])
    p2 = LSTMPropia(epocas=3).fit(textos, y).predict_proba(["sopa fría", "", "😋", "x" * 6000])
    assert np.allclose(p1, p2) and ((p1 >= 0) & (p1 <= 1)).all()
