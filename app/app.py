"""T10 · App: ¿esta reseña de restaurante hay que atenderla? (ADR-07, D31, D35)

Recibe el texto de una reseña y muestra la clase, la probabilidad calibrada y el umbral
aplicado, o "fuera de dominio" con su razón. Usa el modelo congelado de modelos/ a través
del mismo Predictor que se evaluó en prueba. No guarda ni registra lo que se escribe.
Diseño visual adaptado de una propuesta de Stitch (app/estilo.css); todos los números salen del modelo.

Uso:
  uv run python app/app.py          # http://localhost:7860
"""

import html
import os
from pathlib import Path

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")   # sin telemetría: nada sale de la máquina

import gradio as gr  # noqa: E402

from resenas.predictor import Predictor  # noqa: E402

PREDICTOR = Predictor()   # se carga una sola vez al arrancar
CSS = (Path(__file__).parent / "estilo.css").read_text(encoding="utf-8")
HEAD = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800'
        '&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">')

# Ejemplos inventados (no son reseñas reales). La etiqueta de cada chip la calcula el modelo al arrancar.
EJEMPLOS = [
    "Todo muy rico y la atención excelente, aunque el baño estaba sucio y sin papel.",
    "La sopa llegó fría y nos cobraron dos refrescos que nunca pedimos.",
    "Excelente lugar para venir en familia, los tacos al pastor son de lo mejor de la zona.",
    "Un poco caro para mi gusto, pero la comida vale la pena.",
    "Great tacos and friendly staff, we will come back!",
    "asdf 1234",
]

ICONOS = {
    "atender": '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>'
               '<line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    "no_atender": '<polyline points="20 6 9 17 4 12"/>',
    "fuera": '<circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/>',
    "lista": '<line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/>'
             '<line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>',
    "doc": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>'
           '<line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>',
    "check": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
    "candado": '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
}


def svg(nombre: str, tam: int = 16) -> str:
    return (f'<svg width="{tam}" height="{tam}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"'
            f' stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONOS[nombre]}</svg>')


def pct(x: float) -> str:
    return f"{x * 100:.1f} %"


VACIO = (f'<div class="ra-vacio"><div class="ra-vacio-icono">{svg("lista", 26)}</div><div>'
         '<h3>Sin análisis todavía</h3><p>Pega el texto de una reseña o elige uno de los ejemplos y presiona'
         ' <strong>Analizar</strong>.</p></div></div>')


def tarjeta(texto: str) -> str:
    r = PREDICTOR.predecir(texto)
    aviso = f'<div class="ra-aviso">⚠ {html.escape(r.aviso)}</div>' if r.aviso else ""
    meta = f'<div class="ra-meta"><span>Modelo congelado</span><span>Tiempo de respuesta: {r.ms:.1f} ms</span></div>'
    if r.fuera_de_dominio:
        return (f'<article class="ra-card ra-card--fuera" role="status">{aviso}'
                f'<div class="ra-veredicto"><div class="ra-icono">{svg("fuera", 24)}</div><div>'
                '<span class="ra-etiqueta">No se clasifica</span><h3>Fuera de dominio</h3></div></div>'
                f'<div class="ra-razon"><span class="ra-razon-titulo">Razón</span><p>{html.escape(r.razon)}</p>'
                '<div class="ra-instruccion"><strong>Qué hacer:</strong> si es una reseña real, que la revise una persona.</div></div>'
                '<p class="ra-nota">La app sólo clasifica reseñas de restaurantes en español. Antes de usar el modelo, un filtro'
                ' propio revisa que el texto tenga suficientes palabras comunes de las reseñas y del vocabulario del modelo.</p>'
                f'<div class="ra-meta"><span>Umbral aplicado {pct(r.umbral)} · no se llegó a usar</span>'
                f'<span>Tiempo de respuesta: {r.ms:.1f} ms</span></div></article>')

    atender = r.clase == "atender"
    p, u = r.probabilidad, r.umbral
    titulo, etiqueta = ("Atender: reporta un problema", "Mandar al gerente") if atender else \
        ("No hace falta atenderla", "Sin problema reportado")
    frase = (f"La probabilidad ({pct(p)}) es mayor o igual que el umbral ({pct(u)}): se manda al gerente." if atender
             else f"La probabilidad ({pct(p)}) es menor que el umbral ({pct(u)}).")
    posicion = "▲ Arriba del umbral" if atender else "▼ Abajo del umbral"
    return (f'<article class="ra-card ra-card--{r.clase}" role="status">{aviso}'
            f'<div class="ra-veredicto"><div class="ra-icono">{svg(r.clase, 24)}</div><div>'
            f'<span class="ra-etiqueta">{etiqueta}</span><h3>{titulo}</h3></div></div>'
            '<div class="ra-metricas">'
            f'<div class="ra-metrica"><span>Probabilidad de que reporte un problema</span><b class="ra-prob">{pct(p)}</b></div>'
            f'<div class="ra-metrica"><span>Umbral aplicado</span><b>{pct(u)}</b></div></div>'
            '<div class="ra-barra-bloque">'
            '<div class="ra-pista" aria-hidden="true">'
            f'<div class="ra-relleno" style="width:{max(p * 100, 0.6):.1f}%"></div>'
            f'<div class="ra-marca" style="left:{u * 100:.1f}%"><span class="ra-marca-texto">umbral {pct(u)}</span></div></div>'
            '<div class="ra-leyenda"><span>0 %</span><span>probabilidad calibrada</span><span>100 %</span></div>'
            f'<div class="ra-posicion"><span>La barra es la probabilidad; la línea vertical, el umbral.</span><b>{posicion}</b></div></div>'
            f'<div class="ra-frase">{frase}</div>'
            '<p class="ra-nota">El umbral es bajo a propósito: dejar pasar una queja cuesta 10 veces más que leer una reseña de más.</p>'
            f'{meta}</article>')


def contador(texto: str) -> str:
    n = len(texto or "")
    extra = " · se analizarán los primeros 5,000" if n > 5000 else ""
    return f'<div class="ra-contador{" alerta" if n > 5000 else ""}">{n:,} caracteres{extra}</div>'


def construir() -> gr.Blocks:
    clases = {t: PREDICTOR.predecir(t).clase for t in EJEMPLOS}
    with gr.Blocks(title="¿Hay que atender esta reseña?") as demo:
        with gr.Row(elem_classes="ra-top"):
            gr.HTML('<span class="ra-badge">Herramienta operativa · Restaurantes CDMX</span>'
                    '<h1 class="ra-title">¿Hay que atender esta reseña?</h1>'
                    '<p class="ra-subtitle">Pega una reseña de restaurante en español. Te digo si reporta un problema,'
                    ' con qué probabilidad y con qué umbral lo decidí.</p>')
            tema = gr.Button("◐ Claro / oscuro", elem_classes="ra-tema", size="sm", scale=0)

        with gr.Row(elem_classes="ra-grid", equal_height=False):
            with gr.Column(elem_classes="ra-panel", scale=1):
                gr.HTML(f'<div class="ra-panel-head"><h2 class="ra-panel-title">{svg("doc")} Texto de la reseña</h2></div>')
                with gr.Column(elem_classes="ra-cuerpo"):
                    entrada = gr.Textbox(show_label=False, lines=7, max_lines=20, elem_classes="ra-input",
                                         placeholder="Escribe o pega aquí la reseña…")
                    cuenta = gr.HTML(contador(""))
                    with gr.Row(elem_classes="ra-acciones"):
                        analizar = gr.Button("Analizar", elem_classes="ra-analizar", scale=3)
                        borrar = gr.Button("Borrar", elem_classes="ra-borrar", scale=1)
                    gr.HTML('<p class="ra-ejemplos-label">Ejemplos para probar (inventados)</p>')
                    with gr.Column(elem_classes="ra-chips"):
                        chips = [(t, gr.Button(f"“{t}”", elem_classes=["ra-chip", f"ra-chip-{clases[t]}"], size="sm"))
                                 for t in EJEMPLOS]
                    gr.HTML(f'<div class="ra-privacidad">{svg("candado", 15)}<span>No escribas datos personales'
                            ' (nombres, teléfonos, correos). El texto se procesa en el servidor y no se guarda.</span></div>')

            with gr.Column(elem_classes="ra-panel", scale=1):
                gr.HTML(f'<div class="ra-panel-head"><h2 class="ra-panel-title">{svg("check")} Dictamen del modelo</h2>'
                        f'<span class="ra-panel-meta">UMBRAL: {pct(PREDICTOR.umbral)}</span></div>')
                with gr.Column(elem_classes="ra-cuerpo"):
                    salida = gr.HTML(VACIO)

        gr.HTML('<div class="ra-pie"><div>Modelo propio: <strong>TF-IDF + red densa entrenada desde cero, calibrada con'
                ' Platt; sin modelos de lenguaje</strong>. Sólo para reseñas de restaurantes en español.</div>'
                f'<span class="ra-pie-badge">Umbral 3/33 = {pct(PREDICTOR.umbral)} sobre probabilidad calibrada</span></div>')

        analizar.click(tarjeta, inputs=entrada, outputs=salida, show_progress="minimal")
        entrada.submit(tarjeta, inputs=entrada, outputs=salida, show_progress="minimal")
        entrada.change(contador, inputs=entrada, outputs=cuenta, show_progress="hidden")
        borrar.click(lambda: ("", VACIO), outputs=[entrada, salida], show_progress="hidden")
        for texto, chip in chips:
            chip.click(lambda t=texto: t, outputs=entrada, show_progress="hidden").then(
                tarjeta, inputs=entrada, outputs=salida, show_progress="minimal")
        tema.click(None, js="() => { document.body.classList.toggle('dark'); }")
    return demo


if __name__ == "__main__":
    construir().launch(server_name=os.environ.get("HOST", "0.0.0.0"), server_port=int(os.environ.get("PORT", 7860)),
                       share=False, css=CSS, head=HEAD)
