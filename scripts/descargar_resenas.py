"""Descarga reseñas de restaurantes de la CDMX con Google Places API (New).

Cada llamada a Text Search devuelve hasta 20 restaurantes con sus 5 reseñas
"más relevantes", así que una llamada rinde hasta 100 reseñas.

Protecciones para no pagar:
  - Tope duro de llamadas a la API por corrida (--max-llamadas, default 30).
  - Caché en disco (cache/): una consulta ya hecha no se vuelve a pedir.
  - Field mask mínimo: sólo los campos necesarios.
  - Además, en GCP la cuota diaria de la API está limitada.

Salida: data/crudo/resenas_crudas.csv (texto SIN anonimizar; no se versiona).
Siguiente paso: scripts/anonimizar.py.

Uso:
  uv run python scripts/descargar_resenas.py --dry-run          # lista las consultas, 0 llamadas
  uv run python scripts/descargar_resenas.py --consultas 2      # prueba chica
  uv run python scripts/descargar_resenas.py                    # todas las consultas
"""

import argparse
import csv
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from itertools import cycle
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CACHE = RAIZ / "cache"
SALIDA = RAIZ / "data" / "crudo" / "resenas_crudas.csv"
URL = "https://places.googleapis.com/v1/places:searchText"
FIELD_MASK = ",".join([
    "places.id",
    "places.rating",
    "places.userRatingCount",
    "places.primaryType",
    "places.reviews.rating",
    "places.reviews.publishTime",
    "places.reviews.originalText",
])

# Variedad de zonas (nivel socioeconómico y alcaldías distintas) y de tipos de comida.
ZONAS = [
    "Coyoacán", "Roma Norte", "Condesa", "Centro Histórico", "Polanco", "Del Valle",
    "Narvarte", "Doctores", "Tlalpan", "Iztapalapa", "Azcapotzalco", "Santa Fe",
    "Xochimilco", "San Ángel", "Juárez", "Escandón", "Lindavista", "Iztacalco",
    "Gustavo A. Madero", "Tacubaya", "Portales", "Santa María la Ribera",
    "Mixcoac", "Agrícola Oriental", "Venustiano Carranza", "Tláhuac",
    "Cuajimalpa", "Nápoles", "Guerrero", "Anzures",
]
TIPOS = [
    "restaurantes", "taquerías", "fondas de comida corrida", "marisquerías",
    "pizzerías", "restaurantes de comida china", "restaurantes de sushi",
    "cafeterías", "hamburgueserías", "pollerías", "restaurantes de comida rápida",
    "restaurantes buffet", "cantinas", "torterías", "restaurantes vegetarianos",
]


def consultas():
    """Empareja cada zona con un tipo distinto (rotando) para cubrir ambos ejes."""
    tipos = cycle(TIPOS)
    return [f"{next(tipos)} en {zona}, Ciudad de México" for zona in ZONAS]


def leer_key():
    env = RAIZ / ".env"
    if env.exists():
        for linea in env.read_text().splitlines():
            k, _, v = linea.partition("=")
            if k.strip() == "GOOGLE_MAPS_API_KEY":
                return v.strip().strip("'\"")
    key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not key:
        sys.exit("Falta GOOGLE_MAPS_API_KEY en .env")
    return key


def buscar(texto, key, contador, max_llamadas):
    """Devuelve la respuesta JSON de una consulta, desde caché si ya existe."""
    CACHE.mkdir(exist_ok=True)
    archivo = CACHE / (hashlib.sha1(texto.encode()).hexdigest()[:16] + ".json")
    if archivo.exists():
        return json.loads(archivo.read_text()), False
    if contador["llamadas"] >= max_llamadas:
        raise RuntimeError(f"Tope de {max_llamadas} llamadas alcanzado; se detiene.")
    cuerpo = json.dumps({"textQuery": texto, "languageCode": "es", "regionCode": "MX",
                         "pageSize": 20}).encode()
    req = urllib.request.Request(URL, data=cuerpo, method="POST", headers={
        "Content-Type": "application/json",
        "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": FIELD_MASK,
    })
    contador["llamadas"] += 1
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            datos = json.load(r)
    except urllib.error.HTTPError as e:
        detalle = e.read().decode(errors="replace")[:300]
        raise RuntimeError(f"HTTP {e.code} en '{texto}': {detalle}") from None
    archivo.write_text(json.dumps({"consulta": texto, **datos}, ensure_ascii=False))
    time.sleep(0.5)
    return datos, True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--consultas", type=int, default=None, help="usar sólo las primeras N")
    ap.add_argument("--max-llamadas", type=int, default=30)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    lista = consultas()[: args.consultas]
    if args.dry_run:
        print(*lista, sep="\n")
        print(f"\n{len(lista)} consultas → como máximo {len(lista)} llamadas (las que estén en caché no cuentan).")
        return

    key = leer_key()
    contador = {"llamadas": 0}
    lugares, resenas = set(), {}
    for i, texto in enumerate(lista, 1):
        try:
            datos, nueva = buscar(texto, key, contador, args.max_llamadas)
        except RuntimeError as e:
            print(f"⚠ {e}", file=sys.stderr)
            break
        n_antes = len(resenas)
        for p in datos.get("places", []):
            lugares.add(p["id"])
            for r in p.get("reviews", []):
                texto_r = (r.get("originalText") or {}).get("text", "").strip()
                rid = hashlib.sha1(f"{p['id']}|{r.get('publishTime')}|{texto_r}".encode()).hexdigest()[:12]
                resenas[rid] = {
                    "id": rid,
                    "place_id": p["id"],
                    "consulta": texto,
                    "tipo_lugar": p.get("primaryType", ""),
                    "rating_lugar": p.get("rating", ""),
                    "n_resenas_lugar": p.get("userRatingCount", ""),
                    "fecha": (r.get("publishTime") or "")[:10],
                    "estrellas": r.get("rating", ""),
                    "idioma": (r.get("originalText") or {}).get("languageCode", ""),
                    "texto": texto_r,
                }
        origen = "API" if nueva else "caché"
        print(f"[{i:>2}/{len(lista)}] {origen:5} +{len(resenas) - n_antes:>3} reseñas  {texto}")

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    filas = sorted(resenas.values(), key=lambda f: f["fecha"])
    with SALIDA.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()) if filas else ["id"])
        w.writeheader()
        w.writerows(filas)
    print(f"\nLlamadas a la API en esta corrida: {contador['llamadas']}")
    print(f"Restaurantes únicos: {len(lugares)} | reseñas únicas: {len(filas)} → {SALIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
