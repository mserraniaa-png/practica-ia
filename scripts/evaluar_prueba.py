"""T12 · Corrida ÚNICA del modelo congelado sobre prueba (ADR-06, protocolo de D28).

Candado: se niega a correr si
  - algún archivo de modelos/ no coincide con MANIFIESTO.sha256,
  - los datos (resenas, muestra, muestra_prueba, etiquetas) no coinciden con modelos/config.json,
  - hay cambios sin commit en src/, modelos/ o este script,
  - ya existe resultados/prueba/.

Métrica principal: clasificador sobre las 200 de prueba (sin filtro): matriz con el umbral
congelado, costo por 1000, AUC, ECE y curva de fiabilidad, IC 95 % por bootstrap; baselines.
Métrica secundaria: sistema con filtro; una rechazada cuenta como enviada al gerente.

Salida: resultados/prueba/ (resumen.json, tabla.md, probabilidades.csv sin texto, fiabilidad.png).
Después: commit inmediato.

Uso:
  uv run python scripts/evaluar_prueba.py
  uv run python scripts/evaluar_prueba.py --sintetica    # sólo para probar; → resultados/sintetica/prueba/
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402

from resenas import config  # noqa: E402
from resenas.datos import PERMISO_PRUEBA, cargar_etiquetadas  # noqa: E402
from resenas.decision import costo_por_1000, matriz  # noqa: E402
from resenas.metricas import curva_fiabilidad, ece  # noqa: E402
from resenas.predictor import Predictor  # noqa: E402


class CandadoCerrado(RuntimeError):
    pass


def sha256(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def verificar_candado(modelos: Path, datos: Path, salida: Path, revisar_git: bool = True) -> None:
    if salida.exists():
        raise CandadoCerrado(f"Ya existe {salida}: la prueba se corre una sola vez (ADR-06). "
                             "Si hay que corregir algo, va en resultados/prueba_corregida/ con su entrada en DECISIONES.md.")
    for linea in (modelos / "MANIFIESTO.sha256").read_text().splitlines():
        h, nombre = linea.split(maxsplit=1)
        if sha256(modelos / nombre) != h:
            raise CandadoCerrado(f"{nombre} no coincide con el manifiesto del modelo congelado.")
    cfg = json.loads((modelos / "config.json").read_text())
    for nombre, h in cfg["hashes_datos"].items():
        if sha256(datos / nombre) != h:
            raise CandadoCerrado(f"data/{nombre} cambió desde que se congeló el modelo.")
    if revisar_git:
        rutas = ["src", "modelos", "scripts/evaluar_prueba.py"]
        sucio = subprocess.run(["git", "status", "--porcelain", "--", *rutas], cwd=config.RAIZ,
                               capture_output=True, text=True, check=True).stdout.strip()
        if sucio:
            raise CandadoCerrado("Hay cambios sin commit en src/, modelos/ o evaluar_prueba.py:\n" + sucio)


def costo_ic(y, pred, n=2000, semilla=0):
    rng = np.random.default_rng(semilla)
    vals = [costo_por_1000(y[i], pred[i]) for i in (rng.integers(0, len(y), len(y)) for _ in range(n))]
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def ece_ic(y, p, n=2000, semilla=0):
    rng = np.random.default_rng(semilla)
    vals = [ece(y[i], p[i]) for i in (rng.integers(0, len(y), len(y)) for _ in range(n))]
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sintetica", action="store_true")
    args = ap.parse_args()
    if args.sintetica:
        datos, modelos = config.SINTETICA, config.RAIZ / "resultados" / "sintetica" / "modelos"
        salida = config.RAIZ / "resultados" / "sintetica" / "prueba"
    else:
        datos, modelos, salida = config.DATA, config.RAIZ / "modelos", config.RAIZ / "resultados" / "prueba"

    try:
        verificar_candado(modelos, datos, salida, revisar_git=not args.sintetica)
    except CandadoCerrado as e:
        sys.exit(f"⛔ Candado: {e}")

    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=config.RAIZ, capture_output=True, text=True).stdout.strip()
    t0 = time.perf_counter()
    os.environ[PERMISO_PRUEBA] = "1"
    prueba = cargar_etiquetadas(datos, splits=("prueba",))
    del os.environ[PERMISO_PRUEBA]

    pred_obj = Predictor(modelos)
    u = pred_obj.umbral
    y = prueba["y"].to_numpy()
    p = pred_obj.probabilidades(prueba["texto"])
    pred = p >= u
    rechazada = np.array([pred_obj.filtro.evaluar(t).rechazada for t in prueba["texto"]])
    pred_sistema = pred | rechazada            # rechazada → la revisa una persona (cuenta como enviada)
    curva = curva_fiabilidad(y, p)

    baselines = {
        "Nada es atender (mayoritaria)": np.zeros_like(y, dtype=bool),
        "Todo es atender": np.ones_like(y, dtype=bool),
        "≤ 2★ = atender": prueba["estrellas"].to_numpy() <= 2,
    }
    resumen = {
        "fecha": datetime.now().isoformat(timespec="seconds"), "commit": commit, "umbral": u,
        "n": int(len(y)), "atender": int(y.sum()),
        "principal": {"matriz": matriz(y, pred), "costo_1000": costo_por_1000(y, pred), "costo_1000_ic95": costo_ic(y, pred),
                      "auc": float(roc_auc_score(y, p)), "ece": ece(y, p), "ece_ic95": ece_ic(y, p), "fiabilidad": curva},
        "sistema_con_filtro": {"rechazadas": int(rechazada.sum()), "etiqueta_de_rechazadas": y[rechazada].tolist(),
                               "matriz": matriz(y, pred_sistema), "costo_1000": costo_por_1000(y, pred_sistema)},
        "baselines": {k: {"matriz": matriz(y, v), "costo_1000": costo_por_1000(y, v)} for k, v in baselines.items()},
        "segundos": round(time.perf_counter() - t0, 1),
    }

    salida.mkdir(parents=True)
    (salida / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2) + "\n")
    pd.DataFrame({"id": prueba["id"], "y": y, "estrellas": prueba["estrellas"], "p": np.round(p, 4),
                  "atender": pred.astype(int), "rechazada_filtro": rechazada.astype(int)}).to_csv(salida / "probabilidades.csv", index=False)
    m = resumen["principal"]["matriz"]
    lineas = ["| Modelo | Costo / 1000 (min) | VP | FP | FN | VN |", "|---|---|---|---|---|---|"]
    for k, v in resumen["baselines"].items():
        b = v["matriz"]
        lineas.append(f"| {k} | {v['costo_1000']:,.0f} | {b['vp']} | {b['fp']} | {b['fn']} | {b['vn']} |")
    ic = resumen["principal"]["costo_1000_ic95"]
    lineas.append(f"| **Red densa + Platt, umbral {u:.4f}** | **{resumen['principal']['costo_1000']:,.0f}** [{ic[0]:,.0f}, {ic[1]:,.0f}]"
                  f" | {m['vp']} | {m['fp']} | {m['fn']} | {m['vn']} |")
    s = resumen["sistema_con_filtro"]["matriz"]
    lineas.append(f"| Sistema con filtro ({resumen['sistema_con_filtro']['rechazadas']} rechazadas → gerente)"
                  f" | {resumen['sistema_con_filtro']['costo_1000']:,.0f} | {s['vp']} | {s['fp']} | {s['fn']} | {s['vn']} |")
    (salida / "tabla.md").write_text("\n".join(lineas) + "\n")

    fig, ax = plt.subplots(figsize=(5, 4.5))
    ax.plot([0, 1], [0, 1], ls="--", color="gray", lw=1)
    ax.plot([c["p_media"] for c in curva], [c["observada"] for c in curva], marker="o")
    for c in curva:
        ax.annotate(str(c["n"]), (c["p_media"], c["observada"]), fontsize=7, xytext=(3, 3), textcoords="offset points")
    ax.set(xlabel="Probabilidad calibrada", ylabel="Frecuencia observada de atender", xlim=(0, 1), ylim=(0, 1),
           title=f"Prueba: fiabilidad (ECE {resumen['principal']['ece']:.3f})")
    fig.tight_layout()
    fig.savefig(salida / "fiabilidad.png", dpi=150)

    print("\n".join(lineas))
    print(f"\nAUC {resumen['principal']['auc']:.3f} · ECE {resumen['principal']['ece']:.3f}"
          f" [{resumen['principal']['ece_ic95'][0]:.3f}, {resumen['principal']['ece_ic95'][1]:.3f}]"
          f" · commit {commit[:7]} → {salida.relative_to(config.RAIZ)}/")
    if not args.sintetica:
        print("\nAhora: auditoría y commit inmediato de resultados/prueba/.")


if __name__ == "__main__":
    main()
