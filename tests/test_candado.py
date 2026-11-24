"""ADR-06 · evaluar_prueba.py se niega a correr si el modelo o los datos cambiaron, o si ya corrió."""

import importlib.util
import shutil

import pytest

from resenas import config

spec = importlib.util.spec_from_file_location("evaluar_prueba", config.RAIZ / "scripts" / "evaluar_prueba.py")
ep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ep)

MODELOS_SINT = config.RAIZ / "resultados" / "sintetica" / "modelos"


@pytest.fixture
def entorno(tmp_path):
    if not (MODELOS_SINT / "MANIFIESTO.sha256").exists():
        pytest.skip("Falta el modelo sintético: uv run python scripts/congelar.py --sintetica")
    modelos, datos = tmp_path / "modelos", tmp_path / "datos"
    shutil.copytree(MODELOS_SINT, modelos)
    shutil.copytree(config.SINTETICA, datos)
    return modelos, datos, tmp_path / "prueba"


def test_abre_si_todo_coincide(entorno):
    ep.verificar_candado(*entorno, revisar_git=False)


def test_cierra_si_ya_corrió(entorno):
    modelos, datos, salida = entorno
    salida.mkdir()
    with pytest.raises(ep.CandadoCerrado, match="una sola vez"):
        ep.verificar_candado(modelos, datos, salida, revisar_git=False)


def test_cierra_si_cambió_el_modelo(entorno):
    modelos, datos, salida = entorno
    (modelos / "calibrador.json").write_text('{"metodo": "platt", "a": 9, "b": 9}')
    with pytest.raises(ep.CandadoCerrado, match="manifiesto"):
        ep.verificar_candado(modelos, datos, salida, revisar_git=False)


def test_cierra_si_cambiaron_las_etiquetas(entorno):
    modelos, datos, salida = entorno
    with (datos / "etiquetas.csv").open("a") as f:
        f.write("x,1,False,False,1,otra,2026-11-24T00:00:00,1\n")
    with pytest.raises(ep.CandadoCerrado, match="etiquetas.csv"):
        ep.verificar_candado(modelos, datos, salida, revisar_git=False)
