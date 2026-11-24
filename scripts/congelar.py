"""Punto de control B · Congela modelo, calibrador, umbral y filtro de fuera de dominio (ADR-06, D28).

1. Reentrena la red densa con los hiperparámetros de T7 (t7_resumen.json) y verifica que
   reproduce las probabilidades de validación que se evaluaron (probabilidades.csv).
2. Calibrador Platt ajustado con las 200 de validación (D26, opción A).
3. Umbral = teórico 3 / (3 + 30) (D26, opción A).
4. Filtro de fuera de dominio ajustado con las reseñas del periodo de entrenamiento (ADR-05).
5. Escribe modelos/ con config.json y MANIFIESTO.sha256, y verifica que el Predictor
   cargado desde disco da las mismas probabilidades.
No toca la prueba. Se niega a sobrescribir un modelo congelado salvo con --forzar.

Uso:
  uv run python scripts/congelar.py
  uv run python scripts/congelar.py --sintetica      # → resultados/sintetica/modelos/ (no se versiona)
"""

import argparse
import hashlib
import json
import platform
import sys
import time
from datetime import datetime

import numpy as np
import pandas as pd
import sklearn
import torch

from resenas import config
from resenas.calibracion import Platt
from resenas.datos import aptas, cargar_etiquetadas, cargar_resenas, periodo
from resenas.decision import umbral_teorico
from resenas.fuera_dominio import FiltroFueraDominio
from resenas.modelos import RedDensa
from resenas.predictor import Predictor

ARCHIVOS = ["vectorizador.joblib", "red.pt", "calibrador.json", "fuera_dominio.json", "config.json"]


def sha256(ruta) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sintetica", action="store_true")
    ap.add_argument("--forzar", action="store_true")
    args = ap.parse_args()
    carpeta = config.SINTETICA if args.sintetica else config.DATA
    resultados = config.RAIZ / "resultados" / ("sintetica" if args.sintetica else "validacion")
    salida = (resultados / "modelos") if args.sintetica else (config.RAIZ / "modelos")
    if (salida / "MANIFIESTO.sha256").exists() and not args.forzar:
        sys.exit(f"Ya hay un modelo congelado en {salida.relative_to(config.RAIZ)}/. No se sobrescribe sin --forzar"
                 " (y si se hace, se anota en DECISIONES.md).")
    salida.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()

    # 1. Red densa con los hiperparámetros elegidos en T7.
    t7 = json.loads((resultados / "t7_resumen.json").read_text())
    params = next(f["params"] for f in t7["filas"] if f["modelo"].startswith("TF-IDF + red densa"))
    datos = cargar_etiquetadas(carpeta)
    ent, val = datos[datos["split"] == "entrenamiento"], datos[datos["split"] == "validacion"]
    modelo = RedDensa(**params).fit(ent["texto"], ent["y"])
    crudas = modelo.predict_proba(val["texto"])
    evaluadas = pd.read_csv(resultados / "probabilidades.csv", dtype={"id": str}).set_index("id").loc[val["id"], "p_densa"]
    dif = float(np.abs(crudas - evaluadas.to_numpy()).max())
    assert dif < 1e-3, f"El modelo reentrenado no reproduce las probabilidades evaluadas (máx. dif. {dif})"

    # 2–3. Calibrador y umbral (D26, opción A).
    platt = Platt().fit(crudas, val["y"].to_numpy())
    umbral = umbral_teorico()

    # 4. Filtro de fuera de dominio con el periodo de entrenamiento (nunca validación ni prueba).
    todas = aptas(cargar_resenas(carpeta / config.RESENAS))
    textos_ent = todas.loc[periodo(todas["fecha"]) == "entrenamiento", "texto"].tolist()
    filtro = FiltroFueraDominio().ajustar(textos_ent, modelo.vocabulario_palabras())

    # 5. Escribir.
    modelo.guardar(salida)
    (salida / "calibrador.json").write_text(json.dumps({"metodo": "platt", **platt.params()}, indent=2) + "\n")
    (salida / "fuera_dominio.json").write_text(json.dumps(filtro.a_dict(), ensure_ascii=False) + "\n")
    hashes_datos = {f: sha256(carpeta / f) for f in (config.RESENAS, config.MUESTRA, config.MUESTRA_PRUEBA, "etiquetas.csv")}
    cfg = {
        "modelo": "TF-IDF (palabras 1–2 + caracteres 3–5) + red densa", "params": params,
        "calibrador": "platt", "umbral": umbral, "regla_umbral": "teórico 3/(3+30) (D26, opción A)",
        "costos": {"fp": config.COSTO_FP, "fn": config.COSTO_FN}, "semilla": config.SEMILLA,
        "n_entrenamiento": int(len(ent)), "n_validacion_calibrador": int(len(val)),
        "filtro": {"umbral_comunes": filtro.umbral_comunes, "umbral_vocabulario": filtro.umbral_vocabulario,
                   "n_textos_ajuste": len(textos_ent)},
        "hashes_datos": hashes_datos, "fecha": datetime.now().isoformat(timespec="seconds"),
        "versiones": {"python": platform.python_version(), "torch": torch.__version__, "sklearn": sklearn.__version__},
        "decision": "D28",
    }
    (salida / "config.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
    (salida / "MANIFIESTO.sha256").write_text("".join(f"{sha256(salida / a)}  {a}\n" for a in ARCHIVOS))

    # Verificación: el Predictor cargado desde disco reproduce las probabilidades.
    pred = Predictor(salida)
    desde_disco = pred.probabilidades(val["texto"])
    esperadas = platt.transform(crudas)
    assert np.allclose(desde_disco, esperadas, atol=1e-6), "El Predictor desde disco no reproduce las probabilidades"
    rechazadas_val = sum(pred.filtro.evaluar(t).rechazada for t in val["texto"])
    tiempos = [pred.predecir(t).ms for t in val["texto"].head(100)]

    segundos = round(time.perf_counter() - t0, 1)
    print(f"Reproduce lo evaluado: máx. dif. {dif:.1e} · Platt a={platt.params()['a']:.3f} b={platt.params()['b']:.3f}"
          f" · umbral {umbral:.4f}")
    print(f"Filtro: comunes ≥ {filtro.umbral_comunes:.0%}, vocabulario ≥ {filtro.umbral_vocabulario:.0%}"
          f" ({len(textos_ent)} reseñas del periodo de entrenamiento) · rechaza {rechazadas_val}/{len(val)} de validación")
    print(f"Latencia (100 casos, modelo cargado): mediana {np.median(tiempos):.1f} ms · p95 {np.percentile(tiempos, 95):.1f} ms")
    print(f"Atender en validación con el umbral: {(desde_disco >= umbral).sum()}/{len(val)}"
          f" (etiquetadas {int(val['y'].sum())}) · {segundos} s")
    print(f"→ {salida.relative_to(config.RAIZ)}/ :", ", ".join(f"{a} ({(salida / a).stat().st_size / 1e6:.1f} MB)" for a in ARCHIVOS))

    if not args.sintetica:
        tr = config.RAIZ / "resultados" / "tiempos.json"
        t = json.loads(tr.read_text()) if tr.exists() else {}
        t["congelar"] = segundos
        tr.write_text(json.dumps(t, indent=2) + "\n")


if __name__ == "__main__":
    main()
