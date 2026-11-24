# Registro de decisiones

Cada decisión con su cifra o razón y la alternativa que se descartó. Es la fuente del PDF (criterio 5 de la rúbrica). Se agrega una entrada por cada decisión nueva; no se borran las anteriores: si una cambia, se agrega otra que la reemplaza y dice por qué.

## D1 · Datos descargados — 23-nov-2026

- **Decisión:** conservar las 2,783 reseñas ya descargadas (562 restaurantes, 32 llamadas, $0).
- **Razón:** son 4 veces lo que se va a etiquetar (700); lo que sobra sirve para sacar entradas fuera de dominio y casos nuevos.
- **Descartada:** borrarlas y descargar de nuevo con otro tamaño. Gasta cuota y tiempo y da el mismo tipo de datos.

## D2 · Costos de cada error — 23-nov-2026

- **Decisión:** FP = 3 min de gerente; FN = 30 min de gerente (proporción 10:1). El costo esperado se reporta en **minutos por cada 1000 reseñas**.
- **Razón:** un FP es un gerente que lee una reseña que no lo requería (~3 min). Un FN es un problema que nadie atiende: un cliente perdido o daño a la reputación, valuado en ~30 min de gerente (más o menos una cuenta perdida).
- **Descartadas:** costos en pesos (FP $15, FN $400), porque habría que justificar las cifras con una fuente; proporción 20:1, que en el PDF queda como análisis de sensibilidad.

## D3 · Split temporal — 23-nov-2026

- **Decisión:** entrenamiento antes del 1-jul-2026 · validación del 1-jul al 30-sep-2026 · prueba del 1-oct-2026 en adelante.
- **Razón:** el enunciado pide split temporal cuando hay fecha. Con este corte el conjunto de prueba (lo más reciente) tiene 680 reseñas en español con texto, 149 de 1–3★.
- **Descartadas:** corte jun/sep (deja solo ~286 para entrenamiento) y corte ago/mediados de oct (prueba más chica, 492).

## D4 · Cuántas etiquetar y cómo muestrear — 23-nov-2026

- **Decisión:** 700 etiquetadas.
  - Validación: 200 al azar dentro de su periodo.
  - Prueba: 200 al azar dentro de su periodo.
  - Entrenamiento: 300, con 150 de 1–3★ y 150 de 4–5★ (sobremuestreo de quejas).
  - Semilla fija y anotada.
- **Razón:** validación y prueba aleatorias mantienen la proporción real de quejas, así que el costo por 1000 casos es honesto. El sobremuestreo solo en entrenamiento le da al modelo más ejemplos de la clase minoritaria. Se esperan ~45 `atender` en validación y otras ~45 en prueba.
- **Descartadas:** 150+150+300, que deja ~35 quejas por split y vuelve inestables el umbral y la calibración; aleatorio simple en todo, que deja pocas quejas para entrenar; sobremuestreo en todo, que obliga a reponderar los costos y es fácil equivocarse.

## D5 · Restaurante repetido entre splits — 23-nov-2026

- **Decisión:**
  - Se excluyen del conjunto de entrenamiento las reseñas de los restaurantes que tienen alguna reseña etiquetada en validación o prueba.
  - Se excluyen de validación los restaurantes que aparecen en la muestra de prueba.
  - El orden: primero se muestrea prueba, después validación y al final entrenamiento.
- **Razón:** evita que el modelo memorice nombres de platillos o de lugares, y la evaluación mide restaurantes nuevos. Simulado con 20 semillas: el conjunto del que se saca entrenamiento queda en ~865 reseñas (~208 de 1–3★), suficiente para 300.
- **Descartadas:**
  - Excluir todos los restaurantes de los periodos de validación y prueba: deja solo 336 para entrenar.
  - Permitirlo y declararlo: es una fuga que el criterio 2 castiga.
  - Split por restaurante en lugar de por fecha: el enunciado pide split temporal.

## D6 · Herramienta de etiquetado — 23-nov-2026

- **Decisión:** script de terminal (`scripts/etiquetar.py`).
  - Teclas: `1` atender, `0` no atender, `s` ambigua, más una tecla para marcar un nombre que se haya escapado.
  - Guarda después de cada reseña y retoma donde se quedó.
  - Registra quién etiquetó y cuánto tardó en cada reseña.
- **Descartada:** página local en el navegador. Es más cómoda para leer, pero cuesta más construirla.

## D7 · Reseñas ambiguas (`s`) — 23-nov-2026

- **Decisión:** las ambiguas se excluyen del entrenamiento y de la evaluación, se cuentan y se reportan. Se reemplazan con nuevas reseñas del mismo split hasta llegar a las cantidades de D4.
- **Descartada:** forzar una etiqueta, que mete ruido sin decirlo.

## D8 · Menos de 20 errores en prueba — 23-nov-2026 (fijada antes de ver resultados)

- **Decisión:** se analizan todos los errores de prueba y, si son menos de 20, se completa con errores de validación, indicando de qué split viene cada uno.
- **Descartada:** usar solo errores de prueba aunque no lleguen a 20, porque no cumpliría "los 20 casos".

## D9 · Fuera de dominio y reseñas no aptas — 23-nov-2026

- **Decisión:** las 18 reseñas vacías y las que no están en español no se etiquetan ni se usan para entrenar; son candidatas para las 10 entradas fuera de dominio, junto con otras de tipos distintos (galimatías, reseña de hotel o producto, texto muy largo, solo emojis, URL, números).
- **Descartada:** usar solo vacías y en otro idioma, que son dos tipos nada más.

## D10 · Anonimización — 23-nov-2026

- **Decisión:** mientras se etiqueta se marcan los nombres que se hayan escapado; antes de entrenar se cambian por `[PERSONA]`. En el PDF se describe el método (spaCy `es_core_news_sm` + filtro + revisión manual) y cuántas veces falló.
- **Descartadas:** mejorar el filtro antes de etiquetar (retrasa el etiquetado y aun así no queda perfecto); ignorarlo (se podrían colar datos personales en la muestra sintética o en los ejemplos del PDF).

## D11 · Criterios de etiquetado — 23-nov-2026

`atender` = la reseña reporta **un problema concreto que el negocio puede corregir**. Las estrellas no deciden la etiqueta.

| Caso | Etiqueta | Razón | Alternativa descartada |
|---|---|---|---|
| Problema que se resolvió en el momento ("llegó mal pero lo cambiaron rápido") | `atender` | La falla ocurrió y puede repetirse; la etiqueta es "reporta un problema", no "sigue sin resolverse" | `no_atender`: obliga a juzgar si se resolvió bien |
| Precio ("caro pero rico") | `no_atender`, salvo un problema de cobro (cobro de más, cobrar algo que no se sirvió, propina forzada, precio equivocado) | Opinar del precio es cuestión de gusto; un error de cobro es una falla | Toda queja de precio como `atender` |
| Queja vaga ("no me gustó", "nada especial", "no vuelvo") | `no_atender` | No le da al gerente nada que corregir | `atender`: la etiqueta se parecería a "≤ 2★" y el modelo aportaría poco sobre el baseline |
| Reseña positiva con un problema de pasada ("todo bien, aunque el baño estaba sucio") | `atender` | Es justo el caso donde las estrellas fallan y el modelo vale la pena | Solo si es el tema principal |
| Sugerencia sin falla ("estaría bien que tuvieran estacionamiento") | `no_atender` | Es una idea de mejora, no un problema | Contar las sugerencias como `atender` |

Los ejemplos reales de cada caso se agregan en `GUIA_ETIQUETADO.md` (T1).

## D12 · Framework de las redes — 23-nov-2026

- **Decisión:** PyTorch (CPU) para la red densa sobre TF-IDF (modelo entregado) y para la LSTM (alternativa). TF-IDF con scikit-learn. Detalle en ARQUITECTURA.md, ADR-02.
- **Descartadas:** Keras/TensorFlow (instalación más frágil en Mac ARM, app más pesada); MLP de scikit-learn + LSTM en PyTorch (dos estilos de código).

## D13 · Dónde vive la app — 23-nov-2026 (reemplazada por D16)

- **Decisión:** primero local con Gradio, con un comando (ADR-07). Después, si da tiempo, Cloud Run con login de Google vía IAP en el mismo proyecto de GCP (ADR-08), tras un spike de ~1 h.
- **Razón:** el enunciado (§3, §6, rúbrica 1) pide que otra persona la use sin programar y sin uno presente, y que el video lo muestre; no exige publicarla.
- **Descartadas:** Hugging Face Spaces (sin login de Google); liga temporal de Gradio (depende de que la Mac esté prendida).

## D14 · Modelo congelado — 23-nov-2026

- **Decisión:** el modelo, el calibrador, el umbral y el vocabulario se versionan en git con un manifiesto SHA-256; `evaluar_prueba.py` verifica los hashes y se niega a correr dos veces (ADR-06).
- **Descartada:** sólo el manifiesto de hashes, con el modelo fuera de git.

## D15 · Herramienta del PDF — 23-nov-2026

- **Decisión:** Markdown → PDF con pandoc; las cifras y tablas se insertan desde `resultados/` con un script (ADR-09).
- **Descartadas:** LaTeX (más instalación); Google Docs o Word (cifras copiadas a mano).

## D16 · Distribución de la app: contenedor Docker — 23-nov-2026 (reemplaza a D13)

- **Decisión:** la app se entrega como contenedor Docker que **se construye desde el repo** (`docker compose up --build`, o doble clic en `iniciar.command` / `iniciar.bat`), con un README de pasos numerados para alguien que no programa. Sin hosting en la nube. Detalle en ARQUITECTURA.md, ADR-08.
- **Razón:** que otra persona la instale y la use en su máquina sin ayuda (§3, §6) y que funcione igual en Mac, Windows o Linux. Se construye en la máquina de quien la usa, así que no hay que publicar imágenes ni compilar para ARM e Intel.
- **Descartadas:**
  - Cloud Run con login de Google: había que verificar el acceso de cuentas externas y el arranque en frío.
  - Imagen pública en GitHub Container Registry: queda pública y requiere publicar para ARM e Intel.
  - Archivo .tar por Drive: ~1 GB que se regenera con cada cambio.
  - Ejecutable de escritorio: con torch pesa mucho y hay que compilar uno por sistema operativo.

## D17 · Muestra y split congelados — 23-nov-2026 (antes de etiquetar)

- **Decisión:** `scripts/muestrear.py` con semilla **20261123**.
  - Principales: prueba 200, validación 200, entrenamiento 150 de 1–3★ + 150 de 4–5★ (D4).
  - Reservas para reponer las ambiguas (D7): 20 en prueba y 20 en validación. En entrenamiento queda como reserva todo el pool restante: 27 de 1–3★ y 406 de 4–5★.
  - Los restaurantes de las reservas también se excluyen de los splits siguientes (D5), así que reponer una ambigua nunca mete un restaurante en dos splits.
  - Prueba se guarda aparte en `data/muestra_prueba.csv`.
- **Cifras:**
  - Restaurantes por split: prueba 178, validación 169, entrenamiento 205; ninguno se repite.
  - Reseñas de 1–3★ entre las principales: prueba 53, validación 59.
  - Aptas por periodo (español con texto): entrenamiento 1,323 · validación 750 · prueba 689. Corrige las cifras de D3 (1,342 / 757 / 680), que no se pudieron reproducir; el corte de fechas no cambia.
- **Hashes SHA-256:**
  - `data/resenas.csv`: `a94891278d297d249f541970c90698823b962b3f11138fdab38e8b4de495bb8e`
  - `data/muestra.csv`: `ecd95896c8304171d997774a92b2ae388120d7d484106f737cfd6c648434d968`
  - `data/muestra_prueba.csv`: `76225d0a3b4a8bb3884c58d3eb3a7aad259028b1409c1bdb8cdafc1baee7a4c4`
- **Descartadas:** reservas de 40 en prueba y en validación, porque en la simulación con 20 semillas el pool de 1–3★ para entrenamiento bajaba a 159 en el peor caso, contra 150 + reservas que se necesitan; muestra sin reservas, que obliga a muestrear de nuevo cada vez que aparece una ambigua y puede romper D5.

## D18 · Ejemplos de la guía de etiquetado — 23-nov-2026

- **Decisión:** los ejemplos de `GUIA_ETIQUETADO.md` se sacan sólo de las 1,120 reseñas aptas que **no están en la muestra** (ni principales ni reservas) y **no son del periodo de prueba**. En la guía se citan por `id` con una paráfrasis corta, no con el texto.
- **Razón:** si los ejemplos salieran de la muestra, la guía (redactada con ayuda de Claude) estaría proponiendo etiquetas de reseñas que se van a etiquetar, y la regla es que ninguna etiqueta la proponga un modelo. Paráfrasis y no texto porque la guía se versiona y las reseñas no se suben al repo (términos de Google).
- **Descartadas:** ejemplos de la muestra (riesgo de integridad); ejemplos inventados (no muestran los casos difíciles reales); texto literal (publicaría reseñas en git).
- **Pendiente:** aprobar la guía (incluidas R1–R4) y elegir la opción de R5 antes de etiquetar la primera reseña.

## D19 · Guía de etiquetado aprobada — 24-nov-2026 (antes de la primera etiqueta)

- **Decisión:** la etiquetadora aprueba `GUIA_ETIQUETADO.md` v1 con las reglas R1–R4 sin cambios y R5 = opción A.
  - R1: falla verificable de preparación → `atender`; juicio de sabor → `no_atender`.
  - R2: características del local o políticas → `no_atender`, salvo que causen una falla.
  - R3: trato o tiempo con un hecho → `atender`.
  - R4: fallas en pedidos a domicilio o por aplicación → `atender`.
  - R5: queja negativa sin hechos que nombra un área corregible (higiene, trato, tiempo, cobro, estado de la comida) → `atender`; la queja global sin área sigue siendo `no_atender`.
- **Razón de R5:** decirle al gerente *dónde* está el problema ya le da algo que revisar, y este tipo de reseña es común en 1–2★. Mandarla a `no_atender` haría que muchas quejas reales cayeran en falsos negativos, que cuestan 10 veces más (D2).
- **Descartada en R5:** opción B (`no_atender` sin un hecho concreto). Más estricta, pero deja fuera quejas que el negocio sí querría ver.
- **Efecto esperado:** la etiqueta se parece más a "≤ 2★" en las reseñas negativas, lo que puede acercar el baseline de estrellas al modelo. Se revisa con las cifras de T7.

## D20 · Muestra sintética — 24-nov-2026

- **Decisión:** `scripts/generar_sintetica.py` (semilla 7) genera 2,783 reseñas inventadas con fragmentos de plantilla, las mismas columnas y la misma distribución de estrellas y de reseñas por periodo que los datos reales, 18 vacías, 3 en inglés, faltas de ortografía y `[PERSONA]`. Genera la muestra con el mismo código que `muestrear.py` y simula el etiquetado con la lógica de `etiquetar.py` (~3 % de ambiguas). Todo queda en `data/sintetica/`, que sí se versiona.
- **Cifras:** 1,092 lugares; 719 filas de etiquetas, 700 válidas, 19 ambiguas; `atender` ≈ 31 %.
- **Diferencias declaradas con los datos reales:**
  - 1,200 lugares posibles y no 562: aquí los lugares se reparten al azar entre periodos, y con 562 o con 800 la regla D5 dejaba menos de 150 reseñas de 1–3★ para entrenamiento.
  - La proporción de `atender` por estrellas es un supuesto (80 % en 1★ … 7 % en 5★), no una cifra medida.
  - El texto es mucho más regular que el real: **las métricas con la sintética no dicen nada del modelo**; sólo sirve para comprobar que la tubería corre.
- **Descartadas:** sacar la sintética parafraseando reseñas reales (riesgo de reproducir texto real; ver la auditoría de seguridad); generarla con un LLM (no hace falta y complica la regla de integridad).

## D21 · Auditoría de seguridad antes de cada commit — 24-nov-2026

- **Decisión:** `scripts/auditar_seguridad.py --historial` corre antes de cada commit. Busca la key, secretos, correos, teléfonos, place_id, texto de reseñas reales (40 caracteres o más idénticos) y nombres de personas, en lo que entra al commit y en todo el historial. Los nombres que se escapan a la anonimización van en `data/nombres_escapados.txt`, ignorado por git.
- **Razón:** pedido del usuario. La primera corrida encontró 4 paráfrasis de la guía demasiado parecidas a la reseña original; la segunda, los 4 nombres escapados escritos dentro del propio script. Los dos se corrigieron antes de que entraran a git.

## D22 · Etiquetado terminado (T4) y punto de control A — 24-nov-2026

- **Hecho:** 700 etiquetas válidas, de una sola persona (quien entrega la práctica), a mano, con la guía v1, el 24-nov de 13:05 a 14:56.
  - Prueba 200 (42 `atender`, 21 %) · validación 200 (51, 25.5 %) · entrenamiento 150 de 1–3★ + 150 de 4–5★ (77 % y 5 % `atender`).
  - 12 ambiguas, repuestas con reservas (prueba 4, validación 1, entrenamiento 7). 19 reseñas se volvieron a etiquetar con `b`. 14 con un nombre que se escapó (prueba 6, validación 5, entrenamiento 3).
  - Tiempo registrado: 1.19 h sin pausas (731 filas). Mediana 4.3 s por reseña, p95 16.2 s, máximo 43 s.
  - SHA-256 de `data/etiquetas.csv` al cerrar: `f5d12823284b3b1c455942d2164002caed5eb59a3d878eb78c7bcdcd4136a458`.
- **Condiciones del punto A:** ≥ 500 etiquetadas ✔; split congelado ✔ (D17); hash de prueba anotado ✔; tiempo registrado ✔; ≥ 30 `atender` en validación y en prueba ✔.
- **Alerta de calidad (pendiente de decidir):** la velocidad es alta para el largo de las reseñas: mediana de 57 caracteres por segundo; 48 % de las etiquetas a más de 60 car/s (~700 palabras por minuto) y 153 en menos de 2 s. D4 suponía ~5 h para 700. No dice que las etiquetas estén mal, pero hay que medirlo (T5) y declararlo en el PDF.
- **Pendiente:** los 14 nombres marcados todavía no se cambian por `[PERSONA]` (D10).

## D23 · Nombres marcados al etiquetar y consistencia (T5) — 24-nov-2026

- **Nombres (D10):** quien etiquetó revisa las 14 reseñas marcadas con `scripts/revisar_nombres.py` y escribe el nombre que se escapó. Los nombres quedan en `data/nombres_escapados.txt` y, por reseña, en `data/nombres_revisados.csv`; los dos están fuera de git. `anonimizar.py` hace una segunda pasada después de spaCy:
  - en la reseña marcada, el nombre se reemplaza sin distinguir mayúsculas;
  - en las demás, sólo con la grafía exacta, para no tocar palabras comunes.
  - Comprobado con los 4 nombres que se encontraron al hacer la guía: spaCy vuelve a dar los mismos 397 reemplazos, la lista agrega 6, y sólo cambian esas 6 reseñas (ids, fechas, estrellas y lugares iguales).
  - Como cambia el texto de `data/resenas.csv`, cambia su SHA-256 (D17). La muestra no cambia porque depende de ids, fechas, estrellas y lugares. El hash nuevo se anota al terminar.
- **Por qué lo hace la persona y no Claude:** 6 de las 14 reseñas son de prueba, y Claude no lee textos de prueba.
- **T5 (opción A, elegida por el usuario):** `etiquetar.py --repaso` muestra 50 reseñas válidas al azar de los tres splits (lista fija en `data/repaso_ids.csv`), sin la primera etiqueta y sin estrellas, y guarda en `data/repaso.csv`. `scripts/consistencia.py` reporta el % de acuerdo y la κ de Cohen en total, por split y según si la primera etiqueta tomó menos de 2 s.
- **Descartadas:** revisar las 153 de menos de 2 s (opción B): cuesta más y no da una cifra comparable. Sólo declarar la velocidad (opción C): deja el criterio 2 sin evidencia.
- **Regla fijada antes de ver el resultado:** la primera etiqueta es la que vale para entrenar y evaluar; el repaso sólo mide. Si κ < 0.6 se anota aquí y se decide, antes de T7, si se re-etiqueta algo.

## D24 · Resultado de la consistencia (T5) y nombres reemplazados — 24-nov-2026

- **Nombres:** las 14 reseñas marcadas se revisaron, las 14 tenían nombre y la lista manual quedó con 23 nombres. Después de la segunda pasada de `anonimizar.py` hay 431 `[PERSONA]` (antes 403). No queda ningún nombre en las reseñas marcadas ni ninguna aparición exacta de la lista en todo el corpus. `muestrear.py` sigue dando la misma muestra.
  - SHA-256 nuevo de `data/resenas.csv`: `9b807cd23b7038e2fd2a62c6d9b9919ad140affc8ad6cfa958c5b1ee0a854cfc` (reemplaza al de D17; sólo cambió el texto de las reseñas con nombres).
- **Consistencia:** 50 reseñas repasadas el mismo día (15:17–15:21, 3.7 min, mediana 3.7 s), sin ver la primera etiqueta.
  - Acuerdo 90 % (45/50), **κ = 0.72**, IC 95 % por bootstrap [0.45, 0.94]. Cambios: 2 de `no_atender` a `atender` y 3 al revés. Ninguna ambigua.
  - Por split: entrenamiento κ 0.89 (n = 20), prueba 0.76 (n = 15), validación 0.29 (n = 15, 3 desacuerdos; con n tan chico no se interpreta).
  - Las 12 cuya primera etiqueta tomó menos de 2 s coincidieron todas (κ = 1); los 5 desacuerdos están entre las 38 que tomaron 2 s o más. La velocidad alta parece corresponder a casos fáciles, no a descuido.
- **Decisión:** κ ≥ 0.6, el umbral fijado en D23 antes de ver el resultado, así que no se re-etiqueta. Valen las primeras etiquetas.
- **Límites que van al PDF:** el repaso fue el mismo día, menos de 2.5 h después, así que la memoria puede inflar el acuerdo. Es consistencia de una sola persona consigo misma, no acuerdo entre personas ni exactitud. Con n = 50 el intervalo es ancho.
- **Descartada:** repetir el repaso otro día para quitar el efecto de memoria; no cabe en el calendario.
