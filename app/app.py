"""T10 · App: ¿esta reseña de restaurante hay que atenderla? (ADR-07, D31, D35, D37)

Recibe el texto de una reseña y muestra la clase, la probabilidad calibrada y el umbral
aplicado, o "fuera de dominio" con su razón. Usa el modelo congelado de modelos/ a través
del mismo Predictor que se evaluó en prueba. No guarda ni registra lo que se escribe.
Diseño visual tipo editor de documentos (app/estilo.css); todos los números salen del modelo.

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
LIMITE = 5000
MAX_ENTRADA = 20_000   # D40: tope de lo que acepta la caja y el servidor (sólo se analizan 5,000)
MAX_COLA = 20          # D40: peticiones en espera; las demás se rechazan en lugar de amontonarse

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
    "marca": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><polyline points="8 10 11 13 16 8"/>',
    "globo": '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/>'
             '<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "luna": '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>',
}
NOMBRE_CLASE = {"atender": "Atender", "no_atender": "No hace falta", "fuera_de_dominio": "Fuera de dominio"}


def svg(nombre: str, tam: int = 16) -> str:
    return (f'<svg width="{tam}" height="{tam}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"'
            f' stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONOS[nombre]}</svg>')


def pct(x: float) -> str:
    return f"{x * 100:.1f} %"


def _encabezado(icono: str, etiqueta: str = "") -> str:
    tag = f'<span class="ra-tag">{etiqueta}</span>' if etiqueta else ""
    return (f'<header class="ra-sec-head"><span class="ra-sec-icono">{svg(icono, 18)}</span>'
            f'<span class="ra-sec-titulo">Dictamen del modelo</span>{tag}</header>')


def _leyenda(filas: list[tuple[str, str]]) -> str:
    return '<ul class="ra-filas">' + "".join(
        f'<li><span><i class="ra-punto ra-punto-{i}"></i>{k}</span><b>{v}</b></li>' for i, (k, v) in enumerate(filas)
    ) + "</ul>"


def _grande(numero: str, texto: str) -> str:
    return f'<div class="ra-grande"><b>{numero}</b><span>{texto}</span></div>'


VACIO = (f'<section class="ra-sec ra-sec--vacio" role="status">{_encabezado("check")}'
         f'<div class="ra-caja">{_grande("--<sup>%</sup>", "probabilidad de que reporte un problema")}'
         f'{_leyenda([("Umbral aplicado", pct(PREDICTOR.umbral)), ("Decisión", "--"), ("Tiempo", "-- ms")])}</div>'
         '<p class="ra-pista-vacia">Pega una reseña en el editor o elige un ejemplo, y presiona <strong>Analizar</strong>.</p>'
         '</section>')


def tarjeta(texto: str) -> str:
    r = PREDICTOR.predecir((texto or "")[:MAX_ENTRADA])
    aviso = f'<div class="ra-aviso">⚠ {html.escape(r.aviso)}</div>' if r.aviso else ""
    if r.fuera_de_dominio:
        return (f'<section class="ra-sec ra-sec--fuera" data-clase="fuera_de_dominio" role="status">{_encabezado("fuera", "Fuera de dominio")}{aviso}'
                f'<div class="ra-caja">{_grande("No se clasifica", "el texto no parece una reseña de restaurante en español")}'
                f'{_leyenda([("Umbral aplicado (no se usó)", pct(r.umbral)), ("Decisión", "Revisión humana"), ("Tiempo", f"{r.ms:.1f} ms")])}</div>'
                f'<div class="ra-razon"><span class="ra-razon-titulo">Razón</span><p>{html.escape(r.razon)}</p></div>'
                '<div class="ra-frase"><strong>Qué hacer:</strong> si es una reseña real, que la revise una persona.</div>'
                '<p class="ra-nota">Antes de usar el modelo, un filtro propio revisa que el texto tenga suficientes'
                ' palabras comunes de las reseñas y del vocabulario del modelo.</p></section>')

    atender = r.clase == "atender"
    p, u = r.probabilidad, r.umbral
    frase = (f"<strong>Mandar al gerente.</strong> La probabilidad ({pct(p)}) es mayor o igual que el umbral ({pct(u)})."
             if atender else f"<strong>Sin problema reportado.</strong> La probabilidad ({pct(p)}) es menor que el umbral ({pct(u)}).")
    return (f'<section class="ra-sec ra-sec--{r.clase}" data-clase="{r.clase}" data-probabilidad="{p:.4f}" role="status">{_encabezado(r.clase, NOMBRE_CLASE[r.clase])}{aviso}'
            f'<div class="ra-caja">{_grande(f"{p * 100:.1f}<sup>%</sup>", "probabilidad de que reporte un problema")}'
            f'{_leyenda([("Umbral aplicado", pct(u)), ("Decisión", NOMBRE_CLASE[r.clase]), ("Tiempo", f"{r.ms:.1f} ms")])}</div>'
            '<div class="ra-barra-bloque"><div class="ra-pista" aria-hidden="true">'
            f'<div class="ra-relleno" style="width:{max(p * 100, 0.6):.1f}%"></div>'
            f'<div class="ra-marca" style="left:{u * 100:.1f}%"><span class="ra-marca-texto">umbral {pct(u)}</span></div></div>'
            '<div class="ra-leyenda"><span>0 %</span><span>barra = probabilidad · línea = umbral</span><span>100 %</span></div></div>'
            f'<div class="ra-frase">{frase}</div>'
            '<p class="ra-nota">El umbral es bajo a propósito: dejar pasar una queja cuesta 10 veces más que leer una reseña de más.</p>'
            '</section>')


def contador(texto: str) -> str:
    texto = (texto or "")[:MAX_ENTRADA]
    n, palabras = len(texto), len(texto.split())
    extra = f' <span class="ra-alerta">· se analizan los primeros {LIMITE:,}</span>' if n > LIMITE else ""
    return (f'<div class="ra-toolbar-der"><span class="ra-conteo">{palabras:,} palabras · {n:,} caracteres{extra}</span>'
            f'<span class="ra-idioma">{svg("globo", 14)} Sólo español</span></div>')


def construir() -> gr.Blocks:
    clases = {t: PREDICTOR.predecir(t).clase for t in EJEMPLOS}
    with gr.Blocks(title="¿Hay que atender esta reseña?") as demo:
        with gr.Row(elem_classes="ra-top"):
            gr.HTML(f'<div class="ra-logo"><span class="ra-logo-icono">{svg("marca", 20)}</span>'
                    '<span><b>¿Hay que atender esta reseña?</b><small>Restaurantes CDMX · modelo propio</small></span></div>')
            tema = gr.Button("◐ Claro / oscuro", elem_classes="ra-tema", size="sm", scale=0)

        with gr.Column(elem_classes="ra-hoja"):
            with gr.Row(elem_classes="ra-toolbar"):
                gr.HTML(f'<div class="ra-toolbar-izq">{svg("doc", 18)}<span>Texto de la reseña</span></div>')
                cuenta = gr.HTML(contador(""))

            with gr.Row(elem_classes="ra-cuerpo", equal_height=False):
                with gr.Column(elem_classes="ra-editor", scale=3):
                    entrada = gr.Textbox(show_label=False, lines=14, max_lines=40, max_length=MAX_ENTRADA, elem_classes="ra-input",
                                         placeholder="Escribe o pega aquí una reseña de restaurante en español…")
                    with gr.Row(elem_classes="ra-pildora"):
                        borrar = gr.Button("Borrar", elem_classes="ra-borrar", size="sm", scale=0)
                        analizar = gr.Button("Analizar", elem_classes="ra-analizar", size="sm", scale=0)

                with gr.Column(elem_classes="ra-lateral", scale=2):
                    salida = gr.HTML(VACIO)
                    with gr.Column(elem_classes="ra-sec ra-sec--ejemplos"):
                        gr.HTML(f'<header class="ra-sec-head"><span class="ra-sec-icono">{svg("lista", 18)}</span>'
                                '<span class="ra-sec-titulo">Ejemplos para probar</span><span class="ra-tag">inventados</span></header>')
                        chips = [(t, gr.Button(t, elem_classes=["ra-chip", f"ra-chip-{clases[t]}"], size="sm"))
                                 for t in EJEMPLOS]
                    gr.HTML(f'<div class="ra-aviso-pie"><b>{svg("candado", 15)} Sólo reseñas de restaurantes en español</b>'
                            '<span>No escribas datos personales (nombres, teléfonos, correos). El texto se procesa en el'
                            ' servidor y no se guarda. El dictamen ayuda a priorizar; no sustituye la lectura de una persona.</span></div>')

        gr.HTML('<div class="ra-pie"><span>Modelo propio: <strong>TF-IDF + red densa entrenada desde cero, calibrada con'
                ' Platt; sin modelos de lenguaje</strong>.</span>'
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
    construir().queue(max_size=MAX_COLA).launch(server_name=os.environ.get("HOST", "0.0.0.0"), server_port=int(os.environ.get("PORT", 7860)),
                       share=False, css=CSS, head=HEAD)
