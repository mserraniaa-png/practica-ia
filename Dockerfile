# App "¿Hay que atender esta reseña?" (D33): la misma imagen para el respaldo local
# (docker compose up --build) y para el Space de Hugging Face (sdk: docker).
FROM python:3.12.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.1 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1 \
    GRADIO_ANALYTICS_ENABLED=False \
    HOST=0.0.0.0 \
    PORT=7860 \
    RESENAS_RAIZ=/app

# Hugging Face corre los contenedores con el usuario 1000.
RUN useradd -m -u 1000 usuario
WORKDIR /app

# Dependencias primero (capa en caché): sin spaCy ni pytest (--no-default-groups); torch CPU en Linux.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-default-groups --no-install-project

# Sólo lo necesario para predecir: nada de data/, resultados/, .env ni cache/ (ver .dockerignore).
COPY src/ src/
COPY app/ app/
COPY modelos/ modelos/
RUN uv sync --frozen --no-default-groups

USER usuario
EXPOSE 7860
CMD ["/app/.venv/bin/python", "app/app.py"]
