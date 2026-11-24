"""T5 · Consistencia de la etiquetadora: primera etiqueta contra la del repaso.

Entrada:  data/etiquetas.csv, data/repaso.csv (de etiquetar.py --repaso)
Salida:   resultados/etiquetado/consistencia.json (sólo cifras; se versiona)

Reporta % de acuerdo y κ de Cohen, en total, por split y según la velocidad de la
primera etiqueta (< 2 s contra el resto). Las que en el repaso salieron ambiguas se
cuentan aparte y se excluyen del κ.

Uso:
  uv run python scripts/consistencia.py
"""

import argparse
import json

import pandas as pd

from resenas import config
from resenas.etiquetado import cargar_muestra_completa, leer, vigentes
from resenas.metricas import acuerdo, kappa_cohen

SALIDA = config.RAIZ / "resultados" / "etiquetado" / "consistencia.json"


def resumen(df) -> dict:
    return {"n": int(len(df)),
            "acuerdo": round(acuerdo(df["primera"], df["repaso"]), 3) if len(df) else None,
            "kappa": round(kappa_cohen(df["primera"], df["repaso"]), 3) if len(df) else None}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sintetica", action="store_true")
    args = ap.parse_args()
    carpeta = config.SINTETICA if args.sintetica else config.DATA

    etiquetas = leer(carpeta / "etiquetas.csv")
    # La "primera" es la vigente del etiquetado original (incluye correcciones con [b]).
    prim = vigentes(etiquetas)
    seg = etiquetas.drop_duplicates("id", keep="last").set_index("id")["segundos"].astype(float)
    rep = vigentes(leer(carpeta / "repaso.csv"))
    split = cargar_muestra_completa(carpeta).set_index("id")["split"]

    df = pd.DataFrame({"primera": prim.loc[rep.index, "etiqueta"], "repaso": rep["etiqueta"],
                       "segundos_primera": seg.loc[rep.index], "split": split.loc[rep.index]})
    ambiguas = df["repaso"] == ""
    d = df[~ambiguas]

    out = {
        "repasadas": int(len(df)),
        "ambiguas_en_repaso": int(ambiguas.sum()),
        "total": resumen(d),
        "por_split": {s: resumen(g) for s, g in d.groupby("split")},
        "primera_en_menos_de_2s": resumen(d[d["segundos_primera"] < 2]),
        "primera_en_2s_o_mas": resumen(d[d["segundos_primera"] >= 2]),
        "cambios": {f"{a}→{b}": int(n) for (a, b), n in d.groupby(["primera", "repaso"]).size().items() if a != b},
    }
    if not args.sintetica:
        SALIDA.parent.mkdir(parents=True, exist_ok=True)
        SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
