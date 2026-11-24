"""ADR-05 filtro de fuera de dominio y predictor congelado: nunca lanza excepción."""

import json

import numpy as np
import pytest

from resenas.fuera_dominio import FiltroFueraDominio
from resenas.modelos import RedDensa
from resenas.predictor import Predictor

CORPUS = ["la comida estuvo muy rica y el servicio fue amable",
          "el mesero tardó mucho y la sopa llegó fría",
          "muy buen lugar para comer con la familia",
          "nos cobraron de más y el baño estaba sucio",
          "los tacos están muy ricos y el precio es justo"] * 8
Y = [0, 1, 0, 1, 0] * 8
RARAS = ["", "   ", None, 12345, "😋😋😋", "<b>hola</b><script>x</script>", "123 456 789",
         "x" * 10_000, "la comida " * 1500, "Great tacos and friendly staff, will come back",
         "asdf qwer zxcv uiop", "\x00\x01 basura"]


@pytest.fixture(scope="module")
def filtro():
    return FiltroFueraDominio().ajustar(CORPUS, {w for t in CORPUS for w in t.split()})


def test_reglas(filtro):
    assert filtro.evaluar("").razon.startswith("Vacía")
    assert filtro.evaluar("rico").razon.startswith("Muy corta")
    assert filtro.evaluar("Great tacos and friendly staff, will come back").razon.startswith("No parece")
    assert not filtro.evaluar("la sopa llegó fría y el mesero tardó").rechazada


def test_largo_no_rechaza_pero_avisa(filtro):
    v = filtro.evaluar("la comida estuvo muy rica " * 400)
    assert not v.rechazada and "primeros" in v.aviso


def test_ida_y_vuelta(filtro):
    otro = FiltroFueraDominio.de_dict(json.loads(json.dumps(filtro.a_dict())))
    assert all(otro.evaluar(t) == filtro.evaluar(t) for t in CORPUS + RARAS)


@pytest.fixture(scope="module")
def predictor(tmp_path_factory, filtro):
    d = tmp_path_factory.mktemp("modelos")
    m = RedDensa(epocas=5).fit(CORPUS, Y)
    m.guardar(d)
    (d / "calibrador.json").write_text(json.dumps({"metodo": "platt", "a": 1.0, "b": 0.0}))
    (d / "fuera_dominio.json").write_text(json.dumps(filtro.a_dict()))
    (d / "config.json").write_text(json.dumps({"umbral": 3 / 33}))
    return Predictor(d), m


def test_cargado_reproduce_al_entrenado(predictor):
    pred, m = predictor
    assert np.allclose(pred.probabilidades(CORPUS[:5]), m.predict_proba(CORPUS[:5]), atol=1e-6)


@pytest.mark.parametrize("entrada", RARAS)
def test_nunca_lanza_y_siempre_da_umbral(predictor, entrada):
    r = predictor[0].predecir(entrada)
    assert r.umbral == pytest.approx(3 / 33) and r.ms < 2000
    assert r.clase in {"atender", "no_atender", "fuera_de_dominio"}
    assert (r.probabilidad is None) == r.fuera_de_dominio


def test_resena_normal(predictor):
    r = predictor[0].predecir("el mesero tardó mucho y la sopa llegó fría")
    assert not r.fuera_de_dominio and 0 <= r.probabilidad <= 1
