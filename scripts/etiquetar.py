"""T2 · Herramienta de etiquetado en terminal (D6, D7, D10, GUIA_ETIQUETADO.md).

Muestra una reseña a la vez, sin estrellas, en el orden prueba → validación → entrenamiento.
Cada tecla se guarda de inmediato en data/etiquetas.csv; al reabrir sigue donde se quedó.

Teclas:
  1  atender           0  no atender          s  ambigua (se repone con una reserva)
  n  marcar/desmarcar un nombre que se escapó (además hay que etiquetar)
  b  volver a la reseña anterior (se agrega una fila nueva; vale la última)
  p  pausa (el tiempo no corre)        q  salir

Uso:
  uv run python scripts/etiquetar.py --etiquetadora <nombre>   # la primera vez
  uv run python scripts/etiquetar.py                           # después reutiliza el nombre
"""

import argparse
import shutil
import sys
import textwrap
import time
from datetime import datetime
from pathlib import Path

from resenas import config
from resenas.datos import cargar_resenas
from resenas.etiquetado import (ReservasAgotadas, agregar, cargar_muestra_completa, leer,
                                progreso, siguiente, vigentes)

ETIQUETAS = "etiquetas.csv"
VERSION_GUIA = "1"
NOMBRES = {"prueba": "PRUEBA", "validacion": "VALIDACIÓN", "entrenamiento": "ENTRENAMIENTO"}


def leer_tecla() -> str:
    """Una tecla sin Enter si hay terminal; si no (pruebas), una línea de stdin."""
    if not sys.stdin.isatty():
        linea = sys.stdin.readline()
        return linea.strip()[:1] if linea else "q"
    import termios
    import tty
    fd = sys.stdin.fileno()
    antes = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        c = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, antes)
    return "q" if c == "\x03" else c.lower()


def pantalla(fila, texto, prog, etiquetadora, marcado, anterior):
    ancho = min(shutil.get_terminal_size((100, 30)).columns, 100) - 2
    p = prog[fila["split"]]
    total = sum(x["validas"] for x in prog.values())
    objetivo = sum(x["objetivo"] for x in prog.values())
    if sys.stdout.isatty():
        print("\033[2J\033[H", end="")
    print(f"{NOMBRES[fila['split']]} · {p['validas']}/{p['objetivo']} válidas · ambiguas {p['ambiguas']}"
          f" · total {total}/{objetivo} · {etiquetadora}")
    print("─" * ancho)
    for parrafo in texto.splitlines() or [""]:
        print(textwrap.fill(parrafo, ancho) if parrafo.strip() else "")
    print("─" * ancho)
    if anterior is not None:
        print(f"↩ Revisando. Etiqueta anterior: {anterior}")
    print(f"[1] atender  [0] no atender  [s] ambigua  [n] nombre{' ✔ MARCADO' if marcado else ''}"
          f"  [b] atrás  [p] pausa  [q] salir")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--etiquetadora", help="quién etiqueta (se guarda en cada fila)")
    ap.add_argument("--sintetica", action="store_true", help="usar data/sintetica/")
    ap.add_argument("--carpeta", type=Path, help=argparse.SUPPRESS)  # para pruebas
    args = ap.parse_args()

    carpeta = args.carpeta or (config.SINTETICA if args.sintetica else config.DATA)
    ruta = carpeta / ETIQUETAS
    textos = cargar_resenas(carpeta / config.RESENAS).set_index("id")["texto"]
    muestra = cargar_muestra_completa(carpeta)

    etiquetas = leer(ruta)
    etiquetadora = args.etiquetadora or (etiquetas["etiquetadora"].iloc[-1] if len(etiquetas) else "")
    if not etiquetadora:
        sys.exit("Falta --etiquetadora <nombre> (sólo la primera vez).")

    historial = []           # ids etiquetados en esta sesión, para [b]
    revisar = None           # id al que se volvió con [b]
    while True:
        etiquetas = leer(ruta)
        if revisar is not None:
            fila = muestra.set_index("id").loc[revisar].copy()
            fila["id"] = revisar
            anterior = vigentes(etiquetas).loc[revisar, "etiqueta"] or "ambigua"
        else:
            try:
                fila = siguiente(muestra, etiquetas)
            except ReservasAgotadas as e:
                sys.exit(f"⚠ {e}. Anótalo en DECISIONES.md antes de seguir.")
            anterior = None
            if fila is None:
                print("✔ Objetivos de D4 cumplidos. No hay más reseñas que etiquetar.")
                break

        prog = progreso(muestra, etiquetas)
        marcado, pausado, inicio = False, 0.0, time.monotonic()
        while True:
            pantalla(fila, textos[fila["id"]], prog, etiquetadora, marcado, anterior)
            t = leer_tecla()
            if t == "n":
                marcado = not marcado
            elif t == "p":
                p0 = time.monotonic()
                print("⏸ Pausa. Cualquier tecla para seguir.")
                leer_tecla()
                pausado += time.monotonic() - p0
            elif t == "b":
                if not historial:
                    continue
                revisar = historial.pop()
                break
            elif t == "q":
                print(f"Guardado en {ruta}. Hasta luego.")
                return
            elif t in ("1", "0", "s"):
                agregar(ruta, {
                    "id": fila["id"],
                    "etiqueta": "" if t == "s" else t,
                    "ambigua": t == "s",
                    "nombre_escapado": marcado,
                    "segundos": round(time.monotonic() - inicio - pausado, 1),
                    "etiquetadora": etiquetadora,
                    "marca_tiempo": datetime.now().isoformat(timespec="seconds"),
                    "version_guia": VERSION_GUIA,
                })
                if revisar is None:
                    historial.append(fila["id"])
                revisar = None
                break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrumpido; lo etiquetado ya está guardado.")
