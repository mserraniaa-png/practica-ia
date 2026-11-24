"""T2 · orden, reservas, retomar y registro del etiquetado."""

import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from resenas.etiquetado import (COLUMNAS, ReservasAgotadas, agregar, leer, progreso, siguiente, vigentes)

RAIZ = Path(__file__).resolve().parents[1]
OBJ = {("prueba", "aleatorio"): 3, ("validacion", "aleatorio"): 2,
       ("entrenamiento", "1-3"): 2, ("entrenamiento", "4-5"): 2}


def _muestra():
    filas = []
    def bloque(split, estrato, n, reservas, prefijo):
        for i in range(n + reservas):
            filas.append({"id": f"{prefijo}{i}", "split": split, "estrato": estrato, "reserva": i >= n})
    bloque("prueba", "aleatorio", 3, 2, "p")
    bloque("validacion", "aleatorio", 2, 1, "v")
    bloque("entrenamiento", "1-3", 2, 1, "b")
    bloque("entrenamiento", "4-5", 2, 2, "a")
    m = pd.DataFrame(filas)
    # Reservas al final de cada split, como en muestrear.
    m = m.sort_values(["split", "reserva"], kind="stable")
    m["orden"] = m.groupby("split").cumcount() + 1
    return m


def _et(*pares):
    filas = [{"id": i, "etiqueta": "" if e == "s" else e, "ambigua": str(e == "s"), "segundos": "5"}
             for i, e in pares]
    return pd.DataFrame(filas, columns=COLUMNAS).astype(object).fillna("")


def test_empieza_por_prueba_y_sigue_el_orden():
    m = _muestra()
    assert siguiente(m, _et(), OBJ)["id"] == "p0"
    assert siguiente(m, _et(("p0", "1")), OBJ)["id"] == "p1"


def test_pasa_a_validacion_sin_tocar_reservas_si_no_hay_ambiguas():
    m = _muestra()
    assert siguiente(m, _et(("p0", "1"), ("p1", "0"), ("p2", "0")), OBJ)["id"] == "v0"


def test_ambigua_toma_reserva_del_mismo_split():
    m = _muestra()
    et = _et(("p0", "1"), ("p1", "s"), ("p2", "0"))
    assert siguiente(m, et, OBJ)["id"] == "p3"
    assert siguiente(m, pd.concat([et, _et(("p3", "0"))]), OBJ)["id"] == "v0"


def test_ambigua_en_entrenamiento_toma_reserva_del_mismo_estrato():
    m = _muestra()
    hechas = [("p0", "1"), ("p1", "0"), ("p2", "0"), ("v0", "0"), ("v1", "1")]
    ent = [(i, "0") for i in m.loc[(m.split == "entrenamiento") & ~m.reserva, "id"]]
    ent[0] = (ent[0][0], "s")                       # primera principal de entrenamiento, ambigua
    estrato = m.set_index("id").loc[ent[0][0], "estrato"]
    sig = siguiente(m, _et(*hechas, *ent), OBJ)
    assert sig["reserva"] and sig["estrato"] == estrato


def test_vale_la_ultima_fila():
    m = _muestra()
    et = _et(("p0", "1"), ("p1", "s"), ("p2", "0"), ("p1", "1"))   # p1 se corrigió con [b]
    assert siguiente(m, et, OBJ)["id"] == "v0"
    assert vigentes(et).loc["p1", "etiqueta"] == "1"


def test_termina_cuando_se_cumplen_los_objetivos():
    m = _muestra()
    todas = [(i, "0") for i in m.loc[~m.reserva, "id"]]
    assert siguiente(m, _et(*todas), OBJ) is None


def test_reservas_agotadas():
    m = _muestra()
    et = _et(("p0", "s"), ("p1", "s"), ("p2", "s"), ("p3", "s"), ("p4", "s"))
    with pytest.raises(ReservasAgotadas):
        siguiente(m, et, OBJ)


def test_progreso_cuenta_validas_ambiguas_y_atender():
    m = _muestra()
    p = progreso(m, _et(("p0", "1"), ("p1", "s"), ("p2", "0")), OBJ)["prueba"]
    assert (p["validas"], p["ambiguas"], p["atender"], p["objetivo"]) == (2, 1, 1, 3)


def test_agregar_escribe_encabezado_una_vez(tmp_path):
    ruta = tmp_path / "etiquetas.csv"
    agregar(ruta, {"id": "a", "etiqueta": "1"})
    agregar(ruta, {"id": "b", "etiqueta": "0"})
    assert list(leer(ruta)["id"]) == ["a", "b"]


# Criterio de aceptación de T2: etiquetar 10, cerrar, reabrir y que siga en la 11;
# el registro tiene 10 tiempos.
def _carpeta(tmp_path):
    n = 30
    resenas = pd.DataFrame({
        "id": [f"r{i:02d}" for i in range(n)], "lugar": [f"R{i}" for i in range(n)],
        "consulta": "", "tipo_lugar": "", "rating_lugar": "", "fecha": "2026-10-15",
        "estrellas": 5, "idioma": "es", "texto": [f"reseña número {i}" for i in range(n)],
    })
    resenas.to_csv(tmp_path / "resenas.csv", index=False)
    muestra = pd.DataFrame({"id": resenas["id"], "split": "prueba", "estrato": "aleatorio",
                            "orden": range(1, n + 1), "reserva": False, "semilla": 1})
    muestra.head(0).to_csv(tmp_path / "muestra.csv", index=False)
    muestra.to_csv(tmp_path / "muestra_prueba.csv", index=False)
    return tmp_path


def _correr(carpeta, teclas, *extra):
    return subprocess.run(
        [sys.executable, str(RAIZ / "scripts" / "etiquetar.py"), "--carpeta", str(carpeta), *extra],
        input="\n".join(teclas) + "\n", capture_output=True, text=True, check=True)


def test_retoma_donde_se_quedo(tmp_path):
    carpeta = _carpeta(tmp_path)
    teclas = ["1", "0", "n", "1", "s", "0", "x", "1", "0", "0", "1", "0", "q"]
    _correr(carpeta, teclas, "--etiquetadora", "prueba")
    et = leer(carpeta / "etiquetas.csv")
    assert len(et) == 10 and et["segundos"].astype(float).ge(0).all()
    assert et["etiquetadora"].eq("prueba").all()
    assert et.loc[et["id"] == "r02", "nombre_escapado"].item() == "True"
    assert et.loc[et["id"] == "r03", "ambigua"].item() == "True"

    salida = _correr(carpeta, ["q"]).stdout          # reabre sin --etiquetadora
    assert "reseña número 10" in salida


def test_atras_corrige_la_anterior(tmp_path):
    carpeta = _carpeta(tmp_path)
    _correr(carpeta, ["1", "b", "0", "q"], "--etiquetadora", "prueba")
    et = leer(carpeta / "etiquetas.csv")
    assert list(et["id"]) == ["r00", "r00"]
    assert vigentes(et).loc["r00", "etiqueta"] == "0"
