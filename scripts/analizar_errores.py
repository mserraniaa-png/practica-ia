"""T13 · Errores de prueba agrupados por tipo de falla.

Entrada: resultados/prueba/probabilidades.csv (de la corrida única) y
         resultados/prueba/errores_categorias.csv (categorías e hipótesis escritas a mano
         después de la corrida; con paráfrasis, sin texto de reseñas).
Salida:  resultados/prueba/errores.md

No cambia etiquetas ni resultados de prueba: sólo los describe.

Uso:
  uv run python scripts/analizar_errores.py
"""

import json

import pandas as pd

from resenas import config

GRUPOS = {
    "A": "Etiqueta probablemente equivocada según la guía (el modelo detecta una falla que la etiqueta no marcó)",
    "B": "Caso en la frontera de la guía (sabor contra falla, política contra cobro)",
    "C": "Decepción de sabor o precio leída como problema",
    "D": "Reseña positiva o neutral con vocabulario de problemas (espera, logística, ironía, faltas)",
    "E": "Elogio apenas sobre el umbral bajo (0.091): costo aceptado por diseño",
    "F": "Falso negativo: queja corta con negaciones",
}


def main():
    d = config.RAIZ / "resultados" / "prueba"
    p = pd.read_csv(d / "probabilidades.csv", dtype={"id": str})
    c = pd.read_csv(d / "errores_categorias.csv", dtype={"id": str})
    errores = p[p["y"] != p["atender"]]
    assert set(errores["id"]) == set(c["id"]), "Las categorías no cubren exactamente los errores de prueba"
    df = c.merge(p, on="id")
    df["tipo"] = df["y"].map({0: "FP", 1: "FN"})
    assert df["en_los_20"].sum() == 20

    lineas = ["# Análisis de errores en prueba (T13)", "",
              f"Errores: {len(df)} ({(df.tipo == 'FP').sum()} FP, {(df.tipo == 'FN').sum()} FN) de {len(p)} reseñas; "
              f"umbral {json.loads((config.RAIZ / 'modelos' / 'config.json').read_text())['umbral']:.4f}. Categorías e hipótesis escritas después de la corrida única; no se cambió ninguna etiqueta.", "",
              "## Resumen por tipo de falla", "", "| Grupo | Tipo de falla | Errores | En los 20 |", "|---|---|---|---|"]
    for g, nombre in GRUPOS.items():
        s = df[df.grupo == g]
        lineas.append(f"| {g} | {nombre} | {len(s)} | {int(s.en_los_20.sum())} |")
    lineas += ["", "## Los 20 casos más informativos", ""]
    for g, nombre in GRUPOS.items():
        s = df[(df.grupo == g) & (df.en_los_20 == 1)].sort_values("p", ascending=False)
        if s.empty:
            continue
        lineas += [f"### {g}. {nombre}", "", "| id | Tipo | p | ★ | Paráfrasis | Hipótesis de la causa |", "|---|---|---|---|---|---|"]
        for _, x in s.iterrows():
            lineas.append(f"| `{x.id}` | {x.tipo} | {x.p:.3f} | {x.estrellas} | {x.parafrasis} | {x.hipotesis} |")
        lineas.append("")
    (d / "errores.md").write_text("\n".join(lineas) + "\n")
    print("\n".join(lineas[:14]))


if __name__ == "__main__":
    main()
