"""Auditoría de seguridad antes de cada commit.

Revisa lo que entraría al commit (`git add -A --dry-run`) y, con --historial, todo el
historial de git. Busca:
  1. La API key de .env y patrones genéricos de secretos.
  2. Correos y teléfonos.
  3. Texto de reseñas reales (≥ 40 caracteres seguidos iguales a alguna reseña).
  4. Nombres de personas que anonimizar.py quitó de las reseñas, más los de
     data/nombres_escapados.txt (ignorado por git; uno por línea).
  5. place_id de Google.
  6. Archivos sensibles que no estén ignorados (.env, data/, cache/).
  Los .joblib (vectorizador) se revisan por su vocabulario, que viene de reseñas reales.

Nunca imprime la key ni el texto de una reseña. Sale con código 1 si hay hallazgos.

Uso:
  uv run python scripts/auditar_seguridad.py              # lo que entraría al commit
  uv run python scripts/auditar_seguridad.py --historial  # además, todo el historial
"""

import argparse
import difflib
import re
import subprocess
import sys

import pandas as pd

from resenas import config

RAIZ = config.RAIZ
VENTANA = 40
# Falsos positivos revisados a mano (24-nov): palabras comunes que el NER tomó por nombres,
# zonas de la CDMX y el correo noreply de GitHub del autor.
PERMITIDOS = {"Checklist", "Falta", "Ángel", "Gustavo", "Mixcoac", "Comida", "Decepción",
              "mserraniaa-png@users.noreply.github.com", "noreply@anthropic.com", "@pytest.fixture"}
SENSIBLES = [".env", "data/resenas.csv", "data/crudo/resenas_crudas.csv", "data/muestra.csv",
             "data/muestra_prueba.csv", "data/etiquetas.csv", "cache/"]
SECRETOS = {"google_key": r"AIza[0-9A-Za-z_\-]{35}", "llave_privada": r"-----BEGIN [A-Z ]*PRIVATE KEY",
            "asignacion": r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"\s]{8,}"}


def sh(*args):
    return subprocess.run(args, cwd=RAIZ, capture_output=True, text=True, check=True).stdout


def fuentes(historial: bool) -> dict:
    out = {}
    if historial:
        out["historial de git"] = sh("git", "log", "--all", "-p", "--format=commit %H %ae")
    for linea in sh("git", "add", "-A", "--dry-run").splitlines():
        ruta = RAIZ / linea.split("'")[1]
        if ruta.is_file() and ruta.suffix == ".joblib":
            out[str(ruta.relative_to(RAIZ))] = vocabulario_joblib(ruta)
        elif ruta.is_file():
            try:
                out[str(ruta.relative_to(RAIZ))] = ruta.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                out[str(ruta.relative_to(RAIZ))] = ""
    return out


def vocabulario_joblib(ruta) -> str:
    """Vocabulario de un vectorizador guardado (n-gramas de reseñas reales), una entrada por línea."""
    import joblib
    obj = joblib.load(ruta)
    partes = getattr(obj, "transformer_list", [("", obj)])
    return "\n".join(t for _, v in partes for t in getattr(v, "vocabulary_", {}))


def leer_key() -> str:
    env = RAIZ / ".env"
    if not env.exists():
        return ""
    for linea in env.read_text().splitlines():
        k, _, v = linea.partition("=")
        if k.strip() == "GOOGLE_MAPS_API_KEY":
            return v.strip().strip("'\"")
    return ""


def resenas_reales():
    crudo_p, anon_p = RAIZ / "data/crudo/resenas_crudas.csv", RAIZ / "data/resenas.csv"
    if not (crudo_p.exists() and anon_p.exists()):
        return [], set()
    crudo = pd.read_csv(crudo_p, dtype=str).fillna("")
    anon = pd.read_csv(anon_p, dtype=str).fillna("")
    norm = lambda s: re.sub(r"\s+", " ", s.lower())
    textos = [norm(t) for t in pd.concat([crudo["texto"], anon["texto"]]) if len(t) >= VENTANA]
    nombres = set()
    originales = crudo.set_index("id")["texto"]
    for i, b in zip(anon["id"], anon["texto"]):
        if "[PERSONA]" not in b:
            continue
        a = originales[i]
        for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if op == "replace" and "[PERSONA]" in b[j1:j2]:
                nombres.add(a[i1:i2].strip())
    # Nombres que se escaparon a la anonimización: viven fuera de git, uno por línea.
    escapados = RAIZ / "data" / "nombres_escapados.txt"
    if escapados.exists():
        nombres |= {l.strip() for l in escapados.read_text(encoding="utf-8").splitlines() if l.strip()}
    return textos, {n for n in nombres if len(n) >= 3 and n not in PERMITIDOS}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--historial", action="store_true")
    args = ap.parse_args()

    hallazgos = []
    for f in SENSIBLES:
        if subprocess.run(["git", "check-ignore", "-q", f], cwd=RAIZ).returncode != 0:
            hallazgos.append(("NO IGNORADO", f, "archivo sensible fuera de .gitignore"))

    src = fuentes(args.historial)
    key = leer_key()
    textos, nombres = resenas_reales()
    norm = lambda s: re.sub(r"\s+", " ", s.lower())

    for donde, txt in src.items():
        if key and key in txt:
            hallazgos.append(("API KEY", donde, "aparece la key de .env"))
        for nombre, p in SECRETOS.items():
            for m in re.finditer(p, txt):
                hallazgos.append(("secreto", donde, f"{nombre}: {m.group()[:8]}…"))
        correos = {c.lstrip("+") for c in re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", txt)}
        for m in {c for c in correos if not c.startswith("@")} - PERMITIDOS:   # "+@pytest…" de un diff no es correo
            hallazgos.append(("correo", donde, m))
        for m in set(re.findall(r"(?<![\w.])(?:\+?52[\s-]?)?\(?\d{2,3}\)?[\s-]?\d{4}[\s-]?\d{4}(?![\w.])", txt)):
            hallazgos.append(("teléfono", donde, m))
        for m in set(re.findall(r"ChIJ[0-9A-Za-z_\-]{20,}", txt)):
            hallazgos.append(("place_id", donde, m[:10] + "…"))
        t = norm(txt)
        tejas = {t[i:i + VENTANA] for i in range(len(t) - VENTANA + 1)}
        n = sum(any(r[i:i + VENTANA] in tejas for i in range(0, len(r) - VENTANA + 1, 10)) for r in textos)
        if n:
            hallazgos.append(("TEXTO DE RESEÑA", donde, f"{n} reseñas comparten ≥ {VENTANA} caracteres"))
        for nombre in nombres:
            if re.search(rf"(?<!\w){re.escape(nombre)}(?!\w)", txt):
                hallazgos.append(("nombre", donde, nombre))

    print(f"Auditadas {len(src)} fuentes · {len(textos)} reseñas · {len(nombres)} nombres"
          + ("" if textos else " (sin data/: no se pudo comparar contra reseñas reales)"))
    for tipo, donde, detalle in hallazgos:
        print(f"⚠ {tipo:16} {donde}: {detalle}")
    if hallazgos:
        sys.exit(f"{len(hallazgos)} hallazgos: no hacer commit hasta revisarlos.")
    print("✔ Sin hallazgos.")


if __name__ == "__main__":
    main()
