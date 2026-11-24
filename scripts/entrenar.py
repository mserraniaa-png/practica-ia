"""T7 · Baselines, regresión logística (referencia) y red densa sobre TF-IDF, evaluados en validación.

- Hiperparámetros: rejilla chica elegida con validación cruzada de 5 partes DENTRO de
  entrenamiento (agrupada por restaurante), por ROC-AUC (ADR-02).
- Validación: sólo para comparar modelos y barrer el umbral por costo (ADR-04).
  Las probabilidades aquí NO están calibradas; la calibración es T9.
- Prueba: no se carga (cargar_etiquetadas lo bloquea).

Salida (resultados/validacion/, o resultados/sintetica/ con --sintetica):
  probabilidades.csv   id, y, estrellas y probabilidad de cada modelo (sin texto)
  t7_resumen.json      cifras de cada baseline y modelo
  t7_tabla.md          tabla para el PDF
  t7_barrido.png       costo por 1000 contra umbral
  ../tiempos.json      tiempo de cómputo por etapa

Uso:
  uv run python scripts/entrenar.py
  uv run python scripts/entrenar.py --sintetica
"""

import argparse
import itertools
import json
import time

import matplotlib
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from resenas import config  # noqa: E402
from resenas.datos import cargar_etiquetadas  # noqa: E402
from resenas.decision import barrido, costo_por_1000, matriz, mejor_umbral, umbral_teorico  # noqa: E402
from resenas.modelos import Logistica, RedDensa  # noqa: E402

REJILLA_DENSA = [dict(ocultas=o, dropout=d, weight_decay=w)
                 for o, d, w in itertools.product([32, 128], [0.2, 0.5], [1e-4, 1e-3])]   # 8
REJILLA_LOGISTICA = [dict(C=c) for c in (0.3, 1.0, 3.0, 10.0)]


def cv_auc(clase, params, ent) -> float:
    folds = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=config.SEMILLA)
    aucs = []
    for tr, te in folds.split(ent["texto"], ent["y"], groups=ent["lugar"]):
        m = clase(**params).fit(ent["texto"].iloc[tr], ent["y"].iloc[tr])
        aucs.append(roc_auc_score(ent["y"].iloc[te], m.predict_proba(ent["texto"].iloc[te])))
    return float(np.mean(aucs))


def elegir(clase, rejilla, ent):
    filas = [{**p, "cv_auc": cv_auc(clase, p, ent)} for p in rejilla]
    tabla = pd.DataFrame(filas).sort_values("cv_auc", ascending=False)
    mejor = {k: v for k, v in tabla.iloc[0].items() if k != "cv_auc"}
    if "ocultas" in mejor:
        mejor["ocultas"] = int(mejor["ocultas"])
    return mejor, tabla


def resumen_fijo(nombre, y, pred) -> dict:
    return {"modelo": nombre, "umbral": None, "costo_1000": costo_por_1000(y, pred), **matriz(y, pred),
            "auc_val": None}


def resumen_modelo(nombre, y, prob, extra) -> dict:
    tabla = barrido(y, prob)
    mejor = mejor_umbral(tabla)
    u_teo = umbral_teorico()
    return {"modelo": nombre, "umbral": float(mejor["umbral"]), "costo_1000": float(mejor["costo_1000"]),
            **{k: int(mejor[k]) for k in ("vp", "fp", "fn", "vn")},
            "auc_val": float(roc_auc_score(y, prob)),
            "costo_1000_umbral_0.5": costo_por_1000(y, prob >= 0.5),
            f"costo_1000_umbral_teorico_{u_teo:.2f}": costo_por_1000(y, prob >= u_teo),
            **extra}, tabla


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sintetica", action="store_true")
    args = ap.parse_args()
    carpeta = config.SINTETICA if args.sintetica else config.DATA
    salida = config.RAIZ / "resultados" / ("sintetica" if args.sintetica else "validacion")
    salida.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    datos = cargar_etiquetadas(carpeta)
    ent, val = datos[datos["split"] == "entrenamiento"], datos[datos["split"] == "validacion"]
    y = val["y"].to_numpy()
    print(f"Entrenamiento {len(ent)} ({ent['y'].mean():.0%} atender) · validación {len(val)} ({y.mean():.1%} atender)")

    filas, barridos = [], {}
    filas.append(resumen_fijo("Nada es atender (mayoritaria)", y, np.zeros_like(y)))
    filas.append(resumen_fijo("Todo es atender", y, np.ones_like(y)))
    filas.append(resumen_fijo("≤ 2★ = atender", y, val["estrellas"].to_numpy() <= 2))

    probs = pd.DataFrame({"id": val["id"], "y": y, "estrellas": val["estrellas"]})
    for nombre, clave, clase, rejilla in (("Regresión logística (referencia)", "logistica", Logistica, REJILLA_LOGISTICA),
                                          ("TF-IDF + red densa (entregado)", "densa", RedDensa, REJILLA_DENSA)):
        t = time.perf_counter()
        params, tabla_cv = elegir(clase, rejilla, ent)
        modelo = clase(**params).fit(ent["texto"], ent["y"])
        prob = modelo.predict_proba(val["texto"])
        probs[f"p_{clave}"] = np.round(prob, 4)
        fila, barridos[nombre] = resumen_modelo(nombre, y, prob, {
            "params": params, "cv_auc_ent": float(tabla_cv["cv_auc"].iloc[0]),
            "rejilla_cv": tabla_cv.round(4).to_dict("records"), "segundos": round(time.perf_counter() - t, 1)})
        filas.append(fila)
        print(f"{nombre}: {params} · AUC CV ent {fila['cv_auc_ent']:.3f} · AUC val {fila['auc_val']:.3f}"
              f" · umbral {fila['umbral']:.2f} · costo/1000 {fila['costo_1000']:.0f} · {fila['segundos']} s")

    segundos = round(time.perf_counter() - t0, 1)
    resumen = {"n_entrenamiento": len(ent), "n_validacion": len(val), "atender_validacion": int(y.sum()),
               "costos": {"fp": config.COSTO_FP, "fn": config.COSTO_FN}, "umbral_teorico": umbral_teorico(),
               "segundos_total": segundos, "filas": filas,
               "nota": "Umbral elegido y costo medidos sobre la misma validación (optimista); probabilidades sin calibrar (T9)."}
    probs.to_csv(salida / "probabilidades.csv", index=False)
    (salida / "t7_resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2) + "\n")

    lineas = ["| Modelo | Umbral | Costo / 1000 (min) | VP | FP | FN | VN | AUC val |", "|---|---|---|---|---|---|---|---|"]
    for f in filas:
        u = "—" if f["umbral"] is None else f"{f['umbral']:.2f}"
        auc = "—" if f["auc_val"] is None else f"{f['auc_val']:.3f}"
        lineas.append(f"| {f['modelo']} | {u} | {f['costo_1000']:,.0f} | {f['vp']} | {f['fp']} | {f['fn']} | {f['vn']} | {auc} |")
    (salida / "t7_tabla.md").write_text("\n".join(lineas) + "\n")

    fig, ax = plt.subplots(figsize=(7, 4))
    for nombre, tabla in barridos.items():
        ax.plot(tabla["umbral"], tabla["costo_1000"], label=nombre)
    for f in filas[:3]:
        ax.axhline(f["costo_1000"], ls=":", lw=1, color="gray")
        ax.annotate(f["modelo"], (0.99, f["costo_1000"]), ha="right", va="bottom", fontsize=7, color="gray")
    ax.axvline(umbral_teorico(), ls="--", lw=1, color="black")
    ax.set(xlabel="Umbral", ylabel="Costo por 1000 reseñas (min)", title="Validación: costo contra umbral (sin calibrar)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(salida / "t7_barrido.png", dpi=150)

    tiempos_ruta = config.RAIZ / "resultados" / "tiempos.json"
    tiempos = json.loads(tiempos_ruta.read_text()) if tiempos_ruta.exists() else {}
    tiempos["entrenar" + ("_sintetica" if args.sintetica else "")] = segundos
    tiempos_ruta.write_text(json.dumps(tiempos, indent=2) + "\n")

    print("\n" + "\n".join(lineas))
    print(f"\nCómputo: {segundos} s → {salida.relative_to(config.RAIZ)}/")


if __name__ == "__main__":
    main()
