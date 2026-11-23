"""T3 · reglas del split (D3, D4, D5, D7) sobre datos inventados."""

import numpy as np
import pandas as pd
import pytest

from resenas.datos import periodo
from resenas.muestreo import PoolInsuficiente, muestrear, verificar

TAMANOS = dict(n_prueba=40, n_validacion=40, n_por_estrato=30)


@pytest.fixture(scope="module")
def resenas():
    rng = np.random.default_rng(0)
    n = 1500
    fechas = pd.Timestamp("2025-06-01") + pd.to_timedelta(rng.integers(0, 540, n), unit="D")
    df = pd.DataFrame({
        "id": [f"x{i:05d}" for i in range(n)],
        "lugar": [f"R{i:04d}" for i in rng.integers(0, 400, n)],
        "fecha": fechas,
        "estrellas": rng.choice([1, 2, 3, 4, 5], n, p=[.15, .07, .08, .15, .55]),
        "idioma": rng.choice(["es", "en", ""], n, p=[.96, .02, .02]),
        "texto": rng.choice(["la sopa llegó fría", "muy rico todo", ""], n, p=[.45, .5, .05]),
    })
    df.loc[df["idioma"] == "", "texto"] = ""
    return df


@pytest.fixture(scope="module")
def muestra(resenas):
    return muestrear(resenas, semilla=7, reserva=5, **TAMANOS)


def test_cumple_todas_las_reglas(muestra, resenas):
    verificar(muestra, resenas, **TAMANOS)


def test_ningun_restaurante_en_dos_splits(muestra, resenas):
    m = muestra.merge(resenas, on="id")
    assert (m.groupby("lugar")["split"].nunique() == 1).all()


def test_fechas_dentro_de_su_periodo(muestra, resenas):
    m = muestra.merge(resenas, on="id")
    assert (periodo(m["fecha"]) == m["split"]).all()


def test_conteos_y_reservas(muestra):
    principales = muestra[~muestra["reserva"]].groupby(["split", "estrato"]).size()
    assert principales[("prueba", "aleatorio")] == 40
    assert principales[("validacion", "aleatorio")] == 40
    assert principales[("entrenamiento", "1-3")] == 30
    assert principales[("entrenamiento", "4-5")] == 30
    reservas = muestra[muestra["reserva"]].groupby("split").size()
    assert reservas["prueba"] == 5 and reservas["validacion"] == 5


def test_sin_reseñas_vacias_ni_en_otro_idioma(muestra, resenas):
    m = muestra.merge(resenas, on="id")
    assert (m["idioma"] == "es").all() and (m["texto"] != "").all()


def test_reproducible_e_independiente_del_orden_del_csv(resenas, muestra):
    revuelto = resenas.sample(frac=1, random_state=3)
    otra = muestrear(revuelto, semilla=7, reserva=5, **TAMANOS)
    pd.testing.assert_frame_equal(otra.reset_index(drop=True), muestra.reset_index(drop=True))


def test_otra_semilla_da_otra_muestra(resenas, muestra):
    otra = muestrear(resenas, semilla=8, reserva=5, **TAMANOS)
    assert set(otra["id"]) != set(muestra["id"])


def test_falla_si_no_alcanza(resenas):
    with pytest.raises(PoolInsuficiente):
        muestrear(resenas, semilla=7, n_prueba=10_000)


def test_verificar_detecta_restaurante_repetido(muestra, resenas):
    roto = resenas.copy()
    id_val = muestra.loc[muestra["split"] == "validacion", "id"].iloc[0]
    id_pru = muestra.loc[muestra["split"] == "prueba", "id"].iloc[0]
    roto.loc[roto["id"] == id_val, "lugar"] = roto.loc[roto["id"] == id_pru, "lugar"].iloc[0]
    with pytest.raises(AssertionError, match="más de un split"):
        verificar(muestra, roto, **TAMANOS)
