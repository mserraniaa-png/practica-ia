"""Genera o verifica app/referencia.json: la respuesta del predictor a 12 textos inventados.

Sirve para comprobar que el contenedor Docker y el Space dan exactamente lo mismo que el
predictor local (mismo modelo, mismas probabilidades).

Uso:
  uv run python scripts/referencia_app.py --generar
  uv run python scripts/referencia_app.py                       # verifica con el predictor local
  uv run python scripts/referencia_app.py --url http://localhost:7860   # verifica una app corriendo
"""

import argparse
import json
import re
import sys

from resenas import config

RUTA = config.RAIZ / "app" / "referencia.json"
TEXTOS = [
    "Todo muy rico y la atención excelente, aunque el baño estaba sucio y sin papel.",
    "La sopa llegó fría y nos cobraron dos refrescos que nunca pedimos.",
    "Excelente lugar para venir en familia, los tacos al pastor son de lo mejor de la zona.",
    "Un poco caro para mi gusto, pero la comida vale la pena.",
    "El mesero fue grosero y tardaron una hora en traer la comida.",
    "Muy buen café y pan recién hecho, volveremos pronto.",
    "Encontré un cabello en la sopa y nadie se disculpó.",
    "La música estaba muy alta pero la comida muy buena.",
    "Great tacos and friendly staff, we will come back!",
    "",
    "asdf 1234",
    "Pedimos a domicilio y llegó incompleto, faltaron las bebidas.",
]


def local():
    from resenas.predictor import Predictor
    p = Predictor()
    return [{"clase": r.clase, "probabilidad": None if r.probabilidad is None else round(r.probabilidad, 6)}
            for r in map(p.predecir, TEXTOS)]


def remota(url):
    from gradio_client import Client
    c = Client(url, verbose=False)
    out = []
    for t in TEXTOS:
        h = re.sub(r"<[^>]+>", " ", c.predict(t, api_name="/tarjeta"))
        if "Fuera de dominio" in h:
            out.append({"clase": "fuera_de_dominio", "probabilidad": None})
        else:
            prob = float(re.search(r"Probabilidad de que reporte un problema\s+([\d.]+)\s*%", h).group(1)) / 100
            out.append({"clase": "atender" if "Atender:" in h else "no_atender", "probabilidad": prob})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--generar", action="store_true")
    ap.add_argument("--url")
    args = ap.parse_args()
    if args.generar:
        RUTA.write_text(json.dumps({"textos": TEXTOS, "esperado": local()}, ensure_ascii=False, indent=2) + "\n")
        print(f"→ {RUTA.relative_to(config.RAIZ)}")
        return
    esperado = json.loads(RUTA.read_text())["esperado"]
    obtenido = remota(args.url) if args.url else local()
    tol = 0.0006 if args.url else 1e-6          # la app muestra la probabilidad con 1 decimal en %
    malos = [(t, e, o) for t, e, o in zip(TEXTOS, esperado, obtenido)
             if e["clase"] != o["clase"] or (e["probabilidad"] is not None and abs(e["probabilidad"] - o["probabilidad"]) > tol)]
    for t, e, o in malos:
        print(f"✘ {t[:50]!r}: esperado {e}, obtenido {o}")
    print(f"{len(TEXTOS) - len(malos)}/{len(TEXTOS)} coinciden" + (f" ({args.url})" if args.url else " (local)"))
    sys.exit(1 if malos else 0)


if __name__ == "__main__":
    main()
