"""Arma dist/space/ con exactamente lo que se subiría al Space de Hugging Face (D33). NO sube nada.

Copia: Dockerfile, .dockerignore, pyproject.toml, uv.lock, src/resenas/, app/, modelos/ y
space/README.md (tarjeta del Space). Verifica el manifiesto del modelo, que no vaya nada
prohibido y corre la auditoría de seguridad sobre la carpeta.

Uso:
  uv run python scripts/preparar_space.py
Publicar en HF (requiere PRO desde nov-2026; ver D39, hoy se publica en Render):
  uv run hf repo create <usuario>/atender-resenas --repo-type space --space-sdk docker
  uv run hf upload <usuario>/atender-resenas dist/space . --repo-type space
"""

import hashlib
import shutil
import subprocess
import sys

from resenas import config

R = config.RAIZ
DESTINO = R / "dist" / "space"
ARCHIVOS = ["Dockerfile", ".dockerignore", "pyproject.toml", "uv.lock"]
CARPETAS = ["src/resenas", "app", "modelos"]
PROHIBIDO = ("data/", "resultados/", "cache/", ".env", "tests/", "scripts/", ".git/", "__pycache__")


def main():
    for linea in (R / "modelos" / "MANIFIESTO.sha256").read_text().splitlines():
        h, nombre = linea.split(maxsplit=1)
        if hashlib.sha256((R / "modelos" / nombre).read_bytes()).hexdigest() != h:
            sys.exit(f"⛔ modelos/{nombre} no coincide con el manifiesto")
    if DESTINO.exists():
        shutil.rmtree(DESTINO)
    DESTINO.mkdir(parents=True)
    for a in ARCHIVOS:
        shutil.copy2(R / a, DESTINO / a)
    for c in CARPETAS:
        shutil.copytree(R / c, DESTINO / c, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copy2(R / "space" / "README.md", DESTINO / "README.md")

    archivos = sorted(p.relative_to(DESTINO).as_posix() for p in DESTINO.rglob("*") if p.is_file())
    malos = [a for a in archivos if any(x in a or a.startswith(x) for x in PROHIBIDO)]
    if malos:
        sys.exit(f"⛔ Archivos prohibidos en el Space: {malos}")
    total = sum((DESTINO / a).stat().st_size for a in archivos)
    for a in archivos:
        print(f"  {(DESTINO / a).stat().st_size / 1e6:7.2f} MB  {a}")
    print(f"{len(archivos)} archivos, {total / 1e6:.1f} MB → {DESTINO.relative_to(R)}/")
    r = subprocess.run([sys.executable, str(R / "scripts" / "auditar_seguridad.py"), "--carpeta", str(DESTINO.relative_to(R))])
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
