"""D10 · Revisar las reseñas marcadas con [n] y escribir el nombre que se escapó.

Lo corre la persona que etiquetó (incluye reseñas de prueba: Claude no las lee).
Muestra cada reseña marcada (la última etiqueta con nombre_escapado = True) y pide
los nombres, separados por coma. Enter sin texto = no había nombre (marca por error).
Guarda después de cada una y retoma donde se quedó.

Después hay que volver a correr scripts/anonimizar.py para que los reemplace por [PERSONA].

Uso:
  uv run python scripts/revisar_nombres.py
"""

import argparse
import shutil
import textwrap

from resenas import config
from resenas.datos import cargar_resenas
from resenas.etiquetado import leer, vigentes
from resenas.privacidad import guardar_revision, leer_revisados


def main():
    argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()
    textos = cargar_resenas(config.DATA / config.RESENAS).set_index("id")["texto"]
    vig = vigentes(leer(config.DATA / "etiquetas.csv"))
    marcadas = [i for i in vig.index if vig.loc[i, "nombre_escapado"] == "True"]
    revisados = leer_revisados()
    pendientes = [i for i in marcadas if i not in revisados]
    ancho = min(shutil.get_terminal_size((100, 30)).columns, 100) - 2

    print(f"{len(marcadas)} reseñas marcadas · {len(marcadas) - len(pendientes)} ya revisadas · {len(pendientes)} pendientes\n")
    for k, id_ in enumerate(pendientes, 1):
        print("─" * ancho)
        print(f"[{k}/{len(pendientes)}] {id_}")
        print(textwrap.fill(textos[id_], ancho))
        print("─" * ancho)
        while True:
            r = input("Nombre(s) tal como aparecen, separados por coma (Enter = ninguno, q = salir): ").strip()
            if r.lower() == "q":
                print("Guardado. Al volver a correrlo sigue en la siguiente.")
                return
            nombres = {n.strip() for n in r.split(",") if n.strip()}
            faltan = [n for n in nombres if n.lower() not in textos[id_].lower()]
            if faltan:
                print(f"⚠ No encuentro {faltan} en esta reseña; revisa cómo está escrito.")
                continue
            guardar_revision(id_, nombres)
            break
    print("\n✔ Todas revisadas. Ahora: uv run python scripts/anonimizar.py")


if __name__ == "__main__":
    main()
