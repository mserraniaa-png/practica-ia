"""T9 · Calibración y costo honesto, sólo con validación (ADR-03, ADR-04).

Entrada:  resultados/validacion/probabilidades.csv (de entrenar.py; probabilidades sin calibrar)
Salida:   resultados/validacion/t9_resumen.json, t9_tabla.md, t9_fiabilidad.png, t9_barrido.png

Para cada modelo (densa = entregado, logística = referencia) y cada método
(sin calibrar, Platt, isotónica):
  - Probabilidades calibradas fuera de parte (5 partes en validación, agrupadas por restaurante):
    ECE (10 contenedores, IC 95 % por bootstrap), Brier y curva de fiabilidad.
  - Costo honesto por 1000: calibrador y umbral se eligen con 4/5 y el costo se mide en el
    1/5 restante; promedio de 20 particiones. Con umbral barrido y con el teórico 3/33 ≈ 0.09.
Elección para la red densa: la combinación (método, regla de umbral) de menor costo honesto.
El calibrador final se ajusta con las 200 de validación; el umbral final sale de la regla elegida.

Uso:
  uv run python scripts/calibrar.py
  uv run python scripts/calibrar.py --sintetica
"""

import argparse
import json
import time

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from resenas import config  # noqa: E402
from resenas.calibracion import METODOS, costo_honesto, fuera_de_parte  # noqa: E402
from resenas.datos import cargar_etiquetadas  # noqa: E402
from resenas.decision import barrido, mejor_umbral, umbral_teorico  # noqa: E402
from resenas.metricas import bootstrap, brier, curva_fiabilidad, ece  # noqa: E402

REPETICIONES = 20
MODELOS = {"densa": "TF-IDF + red densa (entregado)", "logistica": "Regresión logística (referencia)",
           "lstm": "LSTM con embeddings propios (alternativa)"}
NOMBRE_METODO = {"sin_calibrar": "sin calibrar", "platt": "Platt", "isotonica": "isotónica"}


def costo_promedio(p, y, grupos, metodo, umbral):
    corridas = [costo_honesto(p, y, grupos, metodo, umbral, config.SEMILLA + r) for r in range(REPETICIONES)]
    n = len(y)
    costos = [1000 * (c["fp"] * config.COSTO_FP + c["fn"] * config.COSTO_FN) / n for c in corridas]
    return {"costo_1000": float(np.mean(costos)), "desv": float(np.std(costos)),
            "fp": float(np.mean([c["fp"] for c in corridas])), "fn": float(np.mean([c["fn"] for c in corridas])),
            "umbral_mediano": float(np.median([u for c in corridas for u in c["umbrales"]]))}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sintetica", action="store_true")
    args = ap.parse_args()
    carpeta = config.SINTETICA if args.sintetica else config.DATA
    salida = config.RAIZ / "resultados" / ("sintetica" if args.sintetica else "validacion")

    t0 = time.perf_counter()
    probs = pd.read_csv(salida / "probabilidades.csv", dtype={"id": str})
    val = cargar_etiquetadas(carpeta, splits=("validacion",)).set_index("id")
    grupos = val.loc[probs["id"], "lugar"].to_numpy()
    y = probs["y"].to_numpy()
    u_teo = umbral_teorico()

    resultados, oof = {}, {}
    for clave in MODELOS:
        p = probs[f"p_{clave}"].to_numpy()
        resultados[clave] = {}
        for metodo in METODOS:
            q = p if metodo == "sin_calibrar" else fuera_de_parte(p, y, grupos, metodo, config.SEMILLA)
            oof[(clave, metodo)] = q
            resultados[clave][metodo] = {
                "ece": ece(y, q), "ece_ic95": bootstrap(ece, y, q), "brier": brier(y, q),
                "fiabilidad": curva_fiabilidad(y, q),
                "honesto_barrido": costo_promedio(p, y, grupos, metodo, "barrido"),
                "honesto_teorico": costo_promedio(p, y, grupos, metodo, u_teo),
            }

    # Elección para la red densa: menor costo honesto entre métodos y reglas de umbral.
    opciones = [(m, regla, resultados["densa"][m][f"honesto_{regla}"]["costo_1000"])
                for m in METODOS for regla in ("barrido", "teorico")]
    metodo, regla, _ = min(opciones, key=lambda o: o[2])
    p_densa = probs["p_densa"].to_numpy()
    calibrador = METODOS[metodo]().fit(p_densa, y)
    q = oof[("densa", metodo)]
    umbral = u_teo if regla == "teorico" else float(mejor_umbral(barrido(y, q))["umbral"])
    eleccion = {"metodo": metodo, "regla_umbral": regla, "umbral": round(umbral, 4),
                "calibrador": calibrador.params(),
                "costo_honesto_1000": resultados["densa"][metodo][f"honesto_{regla}"]["costo_1000"]}

    segundos = round(time.perf_counter() - t0, 1)
    resumen = {"n_validacion": int(len(y)), "atender": int(y.sum()), "umbral_teorico": u_teo,
               "repeticiones": REPETICIONES, "eleccion_densa": eleccion, "resultados": resultados,
               "segundos": segundos}
    (salida / "t9_resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2) + "\n")

    lineas = ["| Modelo | Calibración | ECE [IC 95 %] | Brier | Costo honesto / 1000, umbral barrido (± desv) | FP / FN | Costo honesto / 1000, umbral 0.09 | FP / FN |",
              "|---|---|---|---|---|---|---|---|"]
    for clave, nombre in MODELOS.items():
        for m in METODOS:
            r = resultados[clave][m]
            hb, ht = r["honesto_barrido"], r["honesto_teorico"]
            lineas.append(f"| {nombre} | {NOMBRE_METODO[m]} | {r['ece']:.3f} [{r['ece_ic95'][0]:.3f}, {r['ece_ic95'][1]:.3f}]"
                          f" | {r['brier']:.3f} | {hb['costo_1000']:,.0f} (± {hb['desv']:.0f}) | {hb['fp']:.1f} / {hb['fn']:.1f}"
                          f" | {ht['costo_1000']:,.0f} | {ht['fp']:.1f} / {ht['fn']:.1f} |")
    (salida / "t9_tabla.md").write_text("\n".join(lineas) + "\n")

    fig, axs = plt.subplots(1, len(MODELOS), figsize=(5 * len(MODELOS), 4.2))
    for ax, clave in zip(axs, MODELOS):
        ax.plot([0, 1], [0, 1], ls="--", color="gray", lw=1)
        for m in METODOS:
            f = resultados[clave][m]["fiabilidad"]
            ax.plot([x["p_media"] for x in f], [x["observada"] for x in f], marker="o",
                    label=f"{NOMBRE_METODO[m]} (ECE {resultados[clave][m]['ece']:.3f})")
        ax.set(xlabel="Probabilidad predicha", ylabel="Frecuencia observada de atender", title=MODELOS[clave],
               xlim=(0, 1), ylim=(0, 1))
        ax.legend(fontsize=8)
    fig.suptitle("Validación: curva de fiabilidad (calibración fuera de parte)")
    fig.tight_layout()
    fig.savefig(salida / "t9_fiabilidad.png", dpi=150)

    fig, ax = plt.subplots(figsize=(7, 4))
    for m in METODOS:
        t = barrido(y, oof[("densa", m)])
        ax.plot(t["umbral"], t["costo_1000"], label=f"densa, {NOMBRE_METODO[m]}")
    ax.axvline(u_teo, ls="--", color="black", lw=1)
    ax.set(xlabel="Umbral", ylabel="Costo por 1000 reseñas (min)", title="Red densa: costo contra umbral tras calibrar")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(salida / "t9_barrido.png", dpi=150)

    tiempos_ruta = config.RAIZ / "resultados" / "tiempos.json"
    tiempos = json.loads(tiempos_ruta.read_text()) if tiempos_ruta.exists() else {}
    tiempos["calibrar" + ("_sintetica" if args.sintetica else "")] = segundos
    tiempos_ruta.write_text(json.dumps(tiempos, indent=2) + "\n")

    print("\n".join(lineas))
    print(f"\nElección (densa): {NOMBRE_METODO[metodo]}, umbral {regla} = {umbral:.2f},"
          f" costo honesto {eleccion['costo_honesto_1000']:,.0f} min/1000 · {segundos} s")


if __name__ == "__main__":
    main()
