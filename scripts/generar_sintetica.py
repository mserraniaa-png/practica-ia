"""T6 · Muestra sintética con la misma estructura que los datos reales.

Las reseñas se arman con fragmentos de plantilla inventados (ninguna es real) y la
etiqueta se conoce por construcción. Imita la estructura de data/resenas.csv: columnas,
distribución de estrellas, fechas por periodo, reseñas vacías y en otro idioma, y
[PERSONA]. Después genera la muestra con el mismo código que muestrear.py y simula el
etiquetado con la misma lógica de reservas que etiquetar.py.

Salida en data/sintetica/ (sí se versiona):
  resenas.csv, muestra.csv, muestra_prueba.csv, etiquetas.csv

Uso:
  uv run python scripts/generar_sintetica.py
  uv run python scripts/muestrear.py --sintetica     # debe decir "sin cambios"
"""

import hashlib
import io

import numpy as np
import pandas as pd

from resenas import config
from resenas.datos import cargar_resenas
from resenas.etiquetado import COLUMNAS, cargar_muestra_completa, siguiente
from resenas.muestreo import muestrear, verificar

SEMILLA = 7
# Cifras de D17 / PLAN.md "Datos obtenidos" (aptas por periodo y estrellas).
POR_PERIODO = {"entrenamiento": 1323, "validacion": 750, "prueba": 689}
P_ESTRELLAS = [0.107, 0.047, 0.074, 0.144, 0.628]
N_LUGARES = 1200   # más que los 562 reales: aquí los lugares se reparten al azar entre periodos y D5 excluiría demasiados
N_VACIAS, N_INGLES = 18, 3
P_ATENDER = {1: 0.80, 2: 0.75, 3: 0.55, 4: 0.20, 5: 0.07}   # supuesto, sólo para la estructura
P_AMBIGUA = 0.03

ELOGIOS = [
    "La comida estuvo muy rica", "Excelente sazón, como hecho en casa", "Buen lugar para venir en familia",
    "Los tacos al pastor están muy buenos", "El café es delicioso", "La atención fue muy amable",
    "Porciones generosas", "Todo fresco y bien servido", "El ambiente es agradable y tranquilo",
    "Las salsas están buenísimas", "Sirven rápido aunque esté lleno", "La terraza es muy bonita",
    "El pozole vale cada peso", "Muy buenas opciones para desayunar", "La mesera [PERSONA] nos atendió muy bien",
]
PROBLEMAS = [
    "la sopa llegó fría", "tardaron más de una hora en traer la comida", "el mesero fue grosero con nosotros",
    "nos cobraron dos bebidas que no pedimos", "el baño estaba sucio y sin papel", "había un cabello en el plato",
    "el pollo venía crudo por dentro", "nos trajeron un platillo equivocado",
    "la cuenta traía propina incluida sin avisar", "el pedido a domicilio llegó incompleto",
    "las mesas estaban sucias cuando nos sentamos", "nadie nos tomó la orden en veinte minutos",
    "la carne olía mal", "el refresco estaba caliente", "cobran comisión por pagar con tarjeta",
    "la limpieza de la cocina se ve dudosa", "el personal nos ignoró toda la comida",
]
GUSTO = [
    "a mí me pareció algo simple de sabor", "la salsa es demasiado picante para mi gusto", "nada extraordinario",
    "el pan no me encantó", "prefiero los de otra taquería", "es un poco caro pero vale la pena",
    "los precios son algo elevados", "el local es pequeño", "sólo aceptan efectivo", "no hay estacionamiento cerca",
]
SUGERENCIAS = [
    "estaría bien que tuvieran opciones vegetarianas", "podrían poner más mesas afuera",
    "ojalá abrieran más temprano", "sería bueno que aceptaran tarjeta",
]
VAGAS = ["No me gustó.", "Mala experiencia.", "No vuelvo.", "Esperaba más.", "Muy mal."]
CIERRES = ["Recomendado.", "Regresaremos.", "", "", "😋", "👍", "Saludos."]
CONECTORES = [", aunque ", ", pero ", ". Lo único malo: ", ". Eso sí, "]
INGLES = ["Great tacos and friendly staff.", "Food was ok, service was slow.", "Nice place, a bit pricey."]
TIPOS = ["restaurant", "mexican_restaurant", "cafe", "seafood_restaurant", "pizza_restaurant",
         "fast_food_restaurant", "hamburger_restaurant", "sushi_restaurant", "bar"]
ZONAS = ["Coyoacán", "Roma Norte", "Condesa", "Centro Histórico", "Polanco", "Narvarte", "Tlalpan", "Iztapalapa"]
COMIDAS = ["restaurantes", "taquerías", "cafeterías", "marisquerías", "pizzerías", "fondas de comida corrida"]


def ruido(texto: str, rng) -> str:
    """Faltas y estilo de reseña: minúsculas, sin acentos, letras repetidas."""
    if rng.random() < 0.15:
        texto = texto.lower()
    if rng.random() < 0.10:
        texto = texto.translate(str.maketrans("áéíóú", "aeiou"))
    if rng.random() < 0.05:
        texto = texto.replace("muy", "muuuy")
    return texto


def resena(estrellas: int, atender: bool, rng) -> str:
    elige = lambda xs, k=1: list(rng.choice(xs, size=k, replace=False))
    if atender:
        problemas = elige(PROBLEMAS, int(rng.integers(1, 3)))
        if estrellas >= 4:
            cuerpo = elige(ELOGIOS)[0] + rng.choice(CONECTORES) + " y ".join(problemas) + "."
        else:
            cuerpo = (" y ".join(problemas) + ".").capitalize() + (" " + elige(VAGAS)[0] if rng.random() < .4 else "")
    elif estrellas >= 4:
        cuerpo = ". ".join(elige(ELOGIOS, int(rng.integers(1, 3)))) + "."
        if rng.random() < 0.35:
            cuerpo += " " + elige(GUSTO + SUGERENCIAS)[0].capitalize() + "."
    else:
        partes = elige(GUSTO + SUGERENCIAS, int(rng.integers(1, 3)))
        cuerpo = ". ".join(p.capitalize() for p in partes) + "." + (" " + elige(VAGAS)[0] if rng.random() < .5 else "")
    return ruido((cuerpo + " " + rng.choice(CIERRES)).strip(), rng)


def fechas(periodo: str, n: int, rng) -> list:
    inicio, fin = {"entrenamiento": ("2016-07-01", "2026-06-30"),
                   "validacion": ("2026-07-01", "2026-09-30"),
                   "prueba": ("2026-10-01", "2026-11-22")}[periodo]
    if periodo == "entrenamiento":   # la mayoría de 2026, como en los datos reales
        recientes = rng.random(n) < 0.55
        a = np.where(recientes, pd.Timestamp("2026-01-01").value, pd.Timestamp(inicio).value)
        b = np.where(recientes, pd.Timestamp(fin).value, pd.Timestamp("2025-12-31").value)
        valores = rng.integers(a, b)
    else:
        valores = rng.integers(pd.Timestamp(inicio).value, pd.Timestamp(fin).value, n)
    return [pd.Timestamp(v).strftime("%Y-%m-%d") for v in valores]


def generar_resenas(rng) -> tuple[pd.DataFrame, pd.Series]:
    lugares = pd.DataFrame({
        "lugar": [f"S{i:04d}" for i in range(N_LUGARES)],
        "consulta": [f"{rng.choice(COMIDAS)} en {rng.choice(ZONAS)}, Ciudad de México" for _ in range(N_LUGARES)],
        "tipo_lugar": rng.choice(TIPOS, N_LUGARES),
        "rating_lugar": np.round(rng.uniform(3.4, 4.9, N_LUGARES), 1),
    })
    filas, verdad = [], []
    for periodo, n in POR_PERIODO.items():
        for f in fechas(periodo, n, rng):
            e = int(rng.choice([1, 2, 3, 4, 5], p=P_ESTRELLAS))
            atender = bool(rng.random() < P_ATENDER[e])
            filas.append({"fecha": f, "estrellas": e, "idioma": "es", "texto": resena(e, atender, rng)})
            verdad.append(int(atender))
    for i in range(N_VACIAS + N_INGLES):
        vacia = i < N_VACIAS
        filas.append({"fecha": fechas("entrenamiento", 1, rng)[0], "estrellas": int(rng.integers(1, 6)),
                      "idioma": "" if vacia else "en", "texto": "" if vacia else INGLES[i % len(INGLES)]})
        verdad.append(-1)
    df = pd.DataFrame(filas)
    lug = lugares.iloc[rng.integers(0, N_LUGARES, len(df))].reset_index(drop=True)
    df = pd.concat([lug, df], axis=1)
    df["id"] = [hashlib.sha1(f"sint|{i}|{t}".encode()).hexdigest()[:12] for i, t in enumerate(df["texto"])]
    df["etiqueta"] = ""
    verdad = pd.Series(verdad, index=df["id"])
    df = df.sort_values(["fecha", "id"]).reset_index(drop=True)
    columnas = ["id", "lugar", "consulta", "tipo_lugar", "rating_lugar", "fecha", "estrellas", "idioma", "texto", "etiqueta"]
    return df[columnas], verdad


def csv_bytes(df) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False, lineterminator="\n")
    return buf.getvalue().encode("utf-8")


def simular_etiquetado(carpeta, verdad: pd.Series, rng) -> pd.DataFrame:
    """Recorre la muestra con siguiente(), igual que la herramienta, con ~3 % de ambiguas."""
    muestra = cargar_muestra_completa(carpeta)
    filas = []
    etiquetas = pd.DataFrame(columns=COLUMNAS)
    while (fila := siguiente(muestra, etiquetas)) is not None:
        ambigua = rng.random() < P_AMBIGUA
        filas.append({
            "id": fila["id"], "etiqueta": "" if ambigua else str(verdad[fila["id"]]),
            "ambigua": str(ambigua), "nombre_escapado": "False",
            "segundos": str(round(float(rng.gamma(4, 6)), 1)), "etiquetadora": "sintetica",
            "marca_tiempo": "2026-11-24T00:00:00", "version_guia": "1",
        })
        etiquetas = pd.DataFrame(filas, columns=COLUMNAS)
    return etiquetas


def main():
    rng = np.random.default_rng(SEMILLA)
    carpeta = config.SINTETICA
    carpeta.mkdir(parents=True, exist_ok=True)

    resenas, verdad = generar_resenas(rng)
    (carpeta / config.RESENAS).write_bytes(csv_bytes(resenas))

    cargadas = cargar_resenas(carpeta / config.RESENAS)
    muestra = muestrear(cargadas)                       # mismos parámetros que muestrear.py
    verificar(muestra, cargadas)
    es_prueba = muestra["split"] == "prueba"
    (carpeta / config.MUESTRA).write_bytes(csv_bytes(muestra[~es_prueba]))
    (carpeta / config.MUESTRA_PRUEBA).write_bytes(csv_bytes(muestra[es_prueba]))

    etiquetas = simular_etiquetado(carpeta, verdad, rng)
    (carpeta / "etiquetas.csv").write_bytes(csv_bytes(etiquetas))

    validas = etiquetas[etiquetas["etiqueta"] != ""]
    print(f"{len(resenas)} reseñas sintéticas · {resenas['lugar'].nunique()} lugares → {carpeta.relative_to(config.RAIZ)}/")
    print(f"Etiquetas simuladas: {len(etiquetas)} filas, {len(validas)} válidas, "
          f"{(etiquetas['ambigua'] == 'True').sum()} ambiguas, atender = {(validas['etiqueta'] == '1').mean():.0%}")


if __name__ == "__main__":
    main()
