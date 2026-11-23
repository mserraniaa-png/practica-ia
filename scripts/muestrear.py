"""T3 · Muestra y split temporal sin restaurantes repetidos (D3, D4, D5, D7).

Entrada: data/resenas.csv
Salida:  data/muestra.csv          entrenamiento y validación
         data/muestra_prueba.csv   prueba, aparte; su SHA-256 se anota en DECISIONES.md

Sólo escribe ids y metadatos de la muestra: no imprime ni lee para nada el texto de prueba.
Si la muestra ya existe, la recalcula y verifica que sea idéntica; no la sobrescribe
salvo con --forzar (la muestra se congela en el punto de control A).

Uso:
  uv run python scripts/muestrear.py
  uv run python scripts/muestrear.py --sintetica    # con data/sintetica/
"""

import argparse
import hashlib
import io
import sys

from resenas import config
from resenas.datos import cargar_resenas
from resenas.muestreo import PoolInsuficiente, muestrear, verificar


def csv_bytes(df) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False, lineterminator="\n")
    return buf.getvalue().encode("utf-8")


def sha256(datos: bytes) -> str:
    return hashlib.sha256(datos).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sintetica", action="store_true", help="usar data/sintetica/ en vez de data/")
    ap.add_argument("--semilla", type=int, default=config.SEMILLA)
    ap.add_argument("--n-prueba", type=int, default=config.N_PRUEBA)
    ap.add_argument("--n-validacion", type=int, default=config.N_VALIDACION)
    ap.add_argument("--n-por-estrato", type=int, default=config.N_ENTRENAMIENTO_POR_ESTRATO)
    ap.add_argument("--reserva", type=int, default=config.RESERVA)
    ap.add_argument("--forzar", action="store_true", help="sobrescribir una muestra distinta ya existente")
    args = ap.parse_args()

    carpeta = config.SINTETICA if args.sintetica else config.DATA
    entrada = carpeta / config.RESENAS
    resenas = cargar_resenas(entrada)
    tamanos = dict(n_prueba=args.n_prueba, n_validacion=args.n_validacion, n_por_estrato=args.n_por_estrato)

    try:
        muestra = muestrear(resenas, args.semilla, reserva=args.reserva, **tamanos)
    except PoolInsuficiente as e:
        sys.exit(f"No alcanza el pool: {e}")
    resumen = verificar(muestra, resenas, **tamanos)

    es_prueba = muestra["split"] == "prueba"
    salidas = {
        carpeta / config.MUESTRA: csv_bytes(muestra[~es_prueba]),
        carpeta / config.MUESTRA_PRUEBA: csv_bytes(muestra[es_prueba]),
    }
    distintas = [r for r, b in salidas.items() if r.exists() and r.read_bytes() != b]
    if distintas and not args.forzar:
        sys.exit("La muestra ya existe y es distinta: " + ", ".join(str(r.relative_to(config.RAIZ)) for r in distintas)
                 + "\nNo se sobrescribe. Usa --forzar sólo si de verdad hay que rehacerla (y anótalo en DECISIONES.md).")
    for ruta, datos in salidas.items():
        estado = "sin cambios" if ruta.exists() and ruta.read_bytes() == datos else "escrito"
        if estado == "escrito":
            ruta.write_bytes(datos)
        print(f"{ruta.relative_to(config.RAIZ)}: {estado}")

    print(f"\nSemilla: {args.semilla}  ·  reserva en prueba y validación: {args.reserva}")
    print("Principales:", resumen["principales"])
    print("Reservas:   ", resumen["reservas"])
    print("Restaurantes por split:", resumen["restaurantes"])
    print("1–3★ entre las principales:", resumen["bajas_en_principales"])
    print("Verificación: ningún restaurante en dos splits; fechas dentro de su periodo; conteos de D4 ✔")
    print(f"\nSHA-256 {config.RESENAS}:        {sha256(entrada.read_bytes())}")
    print(f"SHA-256 {config.MUESTRA}:         {sha256(salidas[carpeta / config.MUESTRA])}")
    print(f"SHA-256 {config.MUESTRA_PRUEBA}:  {sha256(salidas[carpeta / config.MUESTRA_PRUEBA])}")


if __name__ == "__main__":
    main()
