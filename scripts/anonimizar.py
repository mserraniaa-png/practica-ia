"""Quita datos personales del texto de las reseñas.

- Nombres de personas (meseros, gerentes…) detectados con spaCy es_core_news_sm → [PERSONA]
- Teléfonos, correos y @usuarios → [TELEFONO], [CORREO], [USUARIO]

Entrada:  data/crudo/resenas_crudas.csv
Salida:   data/resenas.csv  (con columna `etiqueta` vacía, lista para etiquetar)

Uso:
  uv run python scripts/anonimizar.py
"""

import re
from pathlib import Path

import pandas as pd
import spacy

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "data" / "crudo" / "resenas_crudas.csv"
SALIDA = RAIZ / "data" / "resenas.csv"

PATRONES = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[CORREO]"),
    (re.compile(r"(?<!\w)@\w{2,}"), "[USUARIO]"),
    (re.compile(r"(?:\+?52[\s-]?)?(?:\(?\d{2,3}\)?[\s-]?)?\d{4}[\s-]?\d{4}"), "[TELEFONO]"),
]
# Lugares que el modelo pequeño confunde con personas.
LUGARES = {"coyoacán", "tehuacán", "polanco", "condesa", "roma", "tlalpan", "xochimilco",
           "iztapalapa", "azcapotzalco", "oaxaca", "puebla", "cdmx", "méxico", "ave maría",
           "alvaro obregon", "álvaro obregón", "mariachi", "jesús", "jesucristo", "dios",
           # comida y otras palabras que también confunde
           "taco", "tacos", "bistec", "costillita", "pastor", "suadero", "michelin",
           "these", "the", "sinaloenses"}


def es_persona(ent):
    """El NER de es_core_news_sm tiene muchos falsos positivos ("Además", "llegó frío").
    Se acepta un PER sólo si todos sus tokens son nombres propios con mayúscula inicial,
    no es un lugar conocido y, si es de una sola palabra, no abre la oración."""
    if ent.label_ != "PER" or ent.text.lower() in LUGARES:
        return False
    if not all(t.is_alpha and t.text[:1].isupper() and t.pos_ == "PROPN" for t in ent):
        return False
    return len(ent) > 1 or not ent[0].is_sent_start


def anonimizar(doc):
    texto = doc.text
    for ent in reversed(doc.ents):
        if es_persona(ent):
            texto = texto[: ent.start_char] + "[PERSONA]" + texto[ent.end_char:]
    for patron, reemplazo in PATRONES:
        texto = patron.sub(reemplazo, texto)
    return texto


def main():
    df = pd.read_csv(ENTRADA, dtype=str).fillna("")
    nlp = spacy.load("es_core_news_sm", disable=["lemmatizer"])
    df["texto"] = [anonimizar(d) for d in nlp.pipe(df["texto"], batch_size=64)]
    n_personas = df["texto"].str.count(r"\[PERSONA\]").sum()

    # place_id se reemplaza por un id corto: basta para agrupar reseñas del mismo lugar.
    df["lugar"] = df["place_id"].astype("category").cat.codes.map(lambda i: f"R{i:04d}")
    columnas = ["id", "lugar", "consulta", "tipo_lugar", "rating_lugar", "fecha",
                "estrellas", "idioma", "texto"]
    df = df[columnas].assign(etiqueta="")

    # Si ya existe un archivo etiquetado, se conservan las etiquetas hechas.
    if SALIDA.exists():
        previas = pd.read_csv(SALIDA, dtype=str).fillna("").set_index("id")["etiqueta"]
        df["etiqueta"] = df["id"].map(previas).fillna("")

    df.to_csv(SALIDA, index=False)
    print(f"{len(df)} reseñas → {SALIDA.relative_to(RAIZ)} | nombres reemplazados: {n_personas}")


if __name__ == "__main__":
    main()
