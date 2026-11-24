"""D10/D23 reemplazo de nombres · T5 repaso y κ."""

import subprocess
import sys

import pandas as pd
import pytest

from resenas.etiquetado import ids_de_repaso, leer
from resenas.metricas import acuerdo, kappa_cohen
from resenas.privacidad import guardar_revision, leer_nombres, leer_revisados, reemplazar

from test_etiquetado import RAIZ, _carpeta


def test_reemplaza_en_la_marcada_sin_importar_mayusculas():
    assert reemplazar("nos atendió fulano, muy bien", set(), {"Fulano"}) == "nos atendió [PERSONA], muy bien"


def test_global_sólo_con_la_grafía_exacta():
    assert reemplazar("Rosa nos sirvió la salsa rosa", {"Rosa"}) == "[PERSONA] nos sirvió la salsa rosa"


def test_no_reemplaza_dentro_de_otra_palabra():
    assert reemplazar("Fulanito y Fulano", {"Fulano"}) == "Fulanito y [PERSONA]"


def test_nombre_compuesto_antes_que_el_simple():
    assert reemplazar("Fulano Mengano y Fulano", {"Fulano", "Fulano Mengano"}) == "[PERSONA] y [PERSONA]"


def test_guardar_revision(tmp_path):
    rev, nom = tmp_path / "rev.csv", tmp_path / "nom.txt"
    guardar_revision("a", {"Fulano"}, rev, nom)
    guardar_revision("b", set(), rev, nom)
    assert leer_revisados(rev) == {"a": {"Fulano"}, "b": set()}
    assert leer_nombres(nom) == {"Fulano"}


def test_kappa():
    assert kappa_cohen([1, 0, 1, 0], [1, 0, 1, 0]) == 1
    assert kappa_cohen([1, 1, 0, 0], [1, 0, 1, 0]) == 0
    assert kappa_cohen([1, 1] + [0] * 8, [1] + [0] * 9) == pytest.approx(0.6154, abs=1e-3)
    assert acuerdo([1, 0], [1, 1]) == 0.5


def test_ids_de_repaso_fijos_y_sólo_válidas(tmp_path):
    et = pd.DataFrame({"id": [f"x{i}" for i in range(80)], "etiqueta": ["1", "0", ""] * 26 + ["1", "0"]})
    ruta = tmp_path / "repaso_ids.csv"
    ids = ids_de_repaso(ruta, et, n=20)
    assert len(ids) == 20 and len(set(ids)) == 20
    assert set(et.set_index("id").loc[ids, "etiqueta"]) <= {"0", "1"}
    assert ids_de_repaso(ruta, et.head(0), n=20) == ids     # se reutiliza la lista guardada


def test_modo_repaso_no_toca_etiquetas_originales(tmp_path):
    carpeta = _carpeta(tmp_path)
    correr = lambda teclas, *extra: subprocess.run(
        [sys.executable, str(RAIZ / "scripts" / "etiquetar.py"), "--carpeta", str(carpeta), *extra],
        input="\n".join(teclas) + "\n", capture_output=True, text=True, check=True).stdout
    correr(["1"] * 20 + ["q"], "--etiquetadora", "prueba")
    antes = (carpeta / "etiquetas.csv").read_bytes()
    salida = correr(["0"] * 30 + ["q"], "--repaso")
    assert (carpeta / "etiquetas.csv").read_bytes() == antes
    assert "Repaso terminado (20)" in salida            # sólo hay 20 válidas
    assert len(leer(carpeta / "repaso.csv")) == 20
