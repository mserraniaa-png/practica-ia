"""T14 · 10 entradas fuera de dominio de tipos distintos (D9): qué responde la app y qué debería.

Las entradas son inventadas (no son reseñas reales). La respuesta esperada se escribió antes
de correr el script. Además se cuentan las reseñas reales vacías y en otro idioma de los datos
(sólo conteos, sin texto).

Salida: resultados/fuera_dominio/tabla.md y resultados.json

Uso:
  uv run python scripts/probar_fuera_dominio.py
"""

import json

import pandas as pd

from resenas import config
from resenas.predictor import Predictor

RECHAZAR, CLASIFICAR = "fuera de dominio", "clasificar normal (con aviso)"
CASOS = [
    ("Vacía", "", RECHAZAR),
    ("Sólo emojis", "😋🔥👍👍🌮", RECHAZAR),
    ("Galimatías", "asdkj qwpoe zmxn alskdj qpwoei lkjhg", RECHAZAR),
    ("Reseña en inglés", "The tacos were amazing but the waiter forgot our drinks twice.", RECHAZAR),
    ("Reseña en portugués", "A comida estava ótima, mas o garçom demorou muito para trazer a conta.", RECHAZAR),
    ("Reseña de hotel (español)", "La habitación estaba sucia, las toallas olían mal y el aire acondicionado no servía.", RECHAZAR),
    ("Reseña de producto (español)", "El celular llegó con la pantalla rota y la batería dura muy poco.", RECHAZAR),
    ("URL y números", "https://www.ejemplo.com 5555 1234 99", RECHAZAR),
    ("HTML / código", "<div><script>alert('hola')</script></div>", RECHAZAR),
    ("Reseña de restaurante muy larga (11,730 caracteres)", "La comida estuvo rica pero el mesero tardó mucho en traer la cuenta. " * 170, CLASIFICAR),
]


def main():
    pred = Predictor()
    filas = []
    for tipo, texto, esperada in CASOS:
        r = pred.predecir(texto)
        respuesta = "fuera de dominio" if r.fuera_de_dominio else f"{r.clase} (p = {r.probabilidad:.2f})"
        ok = r.fuera_de_dominio if esperada == RECHAZAR else not r.fuera_de_dominio
        filas.append({"tipo": tipo, "entrada": texto if len(texto) < 120 else texto[:80] + f"… ({len(texto):,} caracteres)",
                      "responde": respuesta, "razon": r.razon or r.aviso, "deberia": esperada, "coincide": bool(ok),
                      "ms": round(r.ms, 1)})

    # Reseñas reales que no son aptas (D9): sólo conteos.
    reales = pd.read_csv(config.DATA / config.RESENAS, dtype=str).fillna("")
    vacias = reales[reales["texto"].str.strip() == ""]
    otro_idioma = reales[(reales["idioma"] != "es") & (reales["texto"].str.strip() != "")]
    conteo = {"vacias": {"n": len(vacias), "rechazadas": int(sum(pred.predecir(t).fuera_de_dominio for t in vacias["texto"]))},
              "otro_idioma": {"n": len(otro_idioma), "rechazadas": int(sum(pred.predecir(t).fuera_de_dominio for t in otro_idioma["texto"]))}}

    salida = config.RAIZ / "resultados" / "fuera_dominio"
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "resultados.json").write_text(json.dumps({"casos": filas, "reales": conteo}, ensure_ascii=False, indent=2) + "\n")
    lineas = ["| # | Tipo | Entrada (inventada) | Responde la app | Razón o aviso | Debería | ¿Coincide? |", "|---|---|---|---|---|---|---|"]
    for i, f in enumerate(filas, 1):
        entrada = f["entrada"].replace("|", "\\|").replace("<", "&lt;")
        lineas.append(f"| {i} | {f['tipo']} | `{entrada}` | {f['responde']} | {f['razon']} | {f['deberia']} | {'✔' if f['coincide'] else '✘'} |")
    lineas += ["", f"Reseñas reales no aptas (D9): vacías {conteo['vacias']['rechazadas']}/{conteo['vacias']['n']} rechazadas;"
                   f" en otro idioma {conteo['otro_idioma']['rechazadas']}/{conteo['otro_idioma']['n']} rechazadas."]
    (salida / "tabla.md").write_text("\n".join(lineas) + "\n")
    print("\n".join(lineas))


if __name__ == "__main__":
    main()
