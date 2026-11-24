"""T10 · App: ¿esta reseña de restaurante hay que atenderla? (ADR-07)

Recibe el texto de una reseña y muestra la clase, la probabilidad calibrada y el umbral
aplicado, o "fuera de dominio" con su razón. Usa el modelo congelado de modelos/ a través
del mismo Predictor que se evaluó en prueba. No guarda ni registra lo que se escribe.

Uso:
  uv run python app/app.py          # http://localhost:7860
"""

import html
import os

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")   # sin telemetría: nada sale de la máquina

import gradio as gr  # noqa: E402

from resenas.predictor import Predictor  # noqa: E402

PREDICTOR = Predictor()   # se carga una sola vez al arrancar

# Ejemplos inventados (no son reseñas reales).
EJEMPLOS = [
    "Todo muy rico y la atención excelente, aunque el baño estaba sucio y sin papel.",
    "La sopa llegó fría y nos cobraron dos refrescos que nunca pedimos.",
    "Excelente lugar para venir en familia, los tacos al pastor son de lo mejor de la zona.",
    "Un poco caro para mi gusto, pero la comida vale la pena.",
    "Great tacos and friendly staff, we will come back!",
    "asdf 1234",
]

CSS = """
.tarjeta {border-radius: 12px; padding: 18px 20px; border: 1px solid var(--border-color-primary);}
.clase {font-size: 1.6em; font-weight: 700; margin: 0 0 6px;}
.atender {color: #b42318;} .no_atender {color: #067647;} .fuera {color: #93370d;}
.fila {display: flex; justify-content: space-between; margin: 4px 0; font-size: 1.05em;}
.barra {position: relative; height: 16px; background: var(--neutral-200); border-radius: 8px; margin: 14px 0 4px;}
.relleno {position: absolute; left: 0; top: 0; bottom: 0; border-radius: 8px;}
.marca {position: absolute; top: -5px; bottom: -5px; width: 3px; background: #101828;}
.nota {color: var(--body-text-color-subdued); font-size: 0.9em; margin-top: 10px;}
"""


def tarjeta(texto: str) -> str:
    r = PREDICTOR.predecir(texto)
    aviso = f'<div class="nota">⚠ {html.escape(r.aviso)}</div>' if r.aviso else ""
    if r.fuera_de_dominio:
        return (f'<div class="tarjeta"><div class="clase fuera">Fuera de dominio</div>'
                f'<div>{html.escape(r.razon)}</div>'
                f'<div class="fila"><span>Umbral aplicado</span><b>{r.umbral:.1%}</b></div>'
                f'<div class="nota">No se clasifica. Si es una reseña real, que la revise una persona.'
                f' · {r.ms:.0f} ms</div>{aviso}</div>')
    atender = r.clase == "atender"
    titulo = "Atender: reporta un problema" if atender else "No hace falta atenderla"
    color = "#d92d20" if atender else "#12b76a"
    explicacion = (f"La probabilidad ({r.probabilidad:.1%}) es mayor o igual que el umbral ({r.umbral:.1%}): se manda al gerente."
                   if atender else
                   f"La probabilidad ({r.probabilidad:.1%}) es menor que el umbral ({r.umbral:.1%}).")
    return (f'<div class="tarjeta"><div class="clase {r.clase}">{titulo}</div>'
            f'<div class="fila"><span>Probabilidad de que reporte un problema</span><b>{r.probabilidad:.1%}</b></div>'
            f'<div class="fila"><span>Umbral aplicado</span><b>{r.umbral:.1%}</b></div>'
            f'<div class="barra"><div class="relleno" style="width:{r.probabilidad * 100:.1f}%; background:{color}"></div>'
            f'<div class="marca" style="left:{r.umbral * 100:.1f}%"></div></div>'
            f'<div class="nota">{explicacion} El umbral es bajo a propósito: dejar pasar una queja cuesta'
            f' 10 veces más que leer una reseña de más. · {r.ms:.0f} ms</div>{aviso}</div>')


def construir() -> gr.Blocks:
    with gr.Blocks(title="¿Hay que atender esta reseña?") as demo:
        gr.Markdown("# ¿Hay que atender esta reseña?\n"
                    "Pega el texto de una reseña de restaurante (en español). La app dice si reporta un problema"
                    " que el negocio debe atender, con la probabilidad y el umbral aplicado.\n\n"
                    "> **Aviso:** no escribas datos personales (nombres, teléfonos, correos). El texto se procesa"
                    " en el servidor donde corre la app y no se guarda.")
        entrada = gr.Textbox(label="Reseña", lines=6, placeholder="Escribe o pega aquí la reseña…")
        with gr.Row():
            boton = gr.Button("Analizar", variant="primary")
            gr.ClearButton(entrada, value="Borrar")
        salida = gr.HTML()
        gr.Examples(EJEMPLOS, inputs=entrada, label="Ejemplos (inventados)")
        boton.click(tarjeta, inputs=entrada, outputs=salida)
        entrada.submit(tarjeta, inputs=entrada, outputs=salida)
        gr.Markdown("<small>Modelo: TF-IDF + red densa entrenada desde cero, calibrada con Platt; umbral 3/33."
                    " No guarda lo que escribes. Práctica 1, IA aplicada.</small>")
    return demo


if __name__ == "__main__":
    construir().launch(server_name=os.environ.get("HOST", "0.0.0.0"), server_port=int(os.environ.get("PORT", 7860)),
                       share=False, css=CSS)
