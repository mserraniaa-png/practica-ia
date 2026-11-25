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

## D25 · Primer camino completo (T7), en validación — 24-nov-2026

- **Hecho:** `scripts/entrenar.py` con dependencias nuevas en `.venv`: scikit-learn 1.9.1, torch 2.15.0 (CPU; en Linux desde el índice CPU de PyTorch, para la imagen Docker) y matplotlib 3.11.2. Entrenamiento 300 (41 % `atender`, sobremuestreado), validación 200 (51 `atender`, 25.5 %). Prueba no se cargó: `cargar_etiquetadas` la bloquea.
- **Hiperparámetros:** validación cruzada de 5 partes **dentro de entrenamiento**, agrupada por restaurante, por ROC-AUC.
  - Red densa, 8 combinaciones: gana 128 ocultas, dropout 0.5, weight decay 1e-4. AUC CV 0.918; las 8 quedan entre 0.910 y 0.918, así que la diferencia entre ellas es ruido.
  - Logística, 4 valores de C: gana C = 3 (AUC CV 0.909).
- **Validación** (probabilidades sin calibrar; umbral barrido de 0.01 a 0.99):

| Modelo | Umbral | Costo / 1000 | FP | FN | AUC |
|---|---|---|---|---|---|
| Nada es atender | — | 7,650 | 0 | 51 | — |
| Todo es atender (baseline más barato) | — | 2,235 | 149 | 0 | — |
| ≤ 2★ = atender | — | 3,720 | 8 | 24 | — |
| Logística (referencia) | 0.38 | 540 | 36 | 0 | 0.936 |
| Red densa (entregado) | 0.13 | 675 | 45 | 0 | 0.928 |

- **Lectura:**
  - Los dos modelos cuestan entre 3 y 4 veces menos que el mejor baseline. El de estrellas es peor que "todo es atender", porque deja pasar 24 de las 51 quejas.
  - Densa contra logística: 135 min/1000 de diferencia son 9 FP en 200 reseñas, dentro del ruido. La densa es menos sensible al umbral (curva más plana en `t7_barrido.png`) y es el modelo que pide el enunciado; la logística queda como referencia.
  - **El costo de esta tabla es optimista:** el umbral se eligió en la misma validación donde se mide, y con 51 positivos cae justo donde no hay FN. La cifra honesta sale en T9, con validación cruzada dentro de validación.
  - Sin calibrar, el umbral de la densa (0.13) está cerca del teórico 0.09; con el teórico costaría 810. La logística en el teórico cuesta 1,920. Se revisa en T9.
- **Cómputo:** 21.7 s en total (CPU, Mac), en `resultados/tiempos.json`.
- **Descartadas:** elegir hiperparámetros con validación (contaminaría la comparación y el umbral); umbral 0.5 (1,365 la densa y 1,500 la logística, el doble o más).

## D26 · Calibración y costo honesto (T9), sólo con validación — 24-nov-2026

- **Método:** `scripts/calibrar.py`.
  - Las probabilidades calibradas se obtienen fuera de parte: 5 partes dentro de validación, agrupadas por restaurante.
  - Costo honesto: en cada parte, calibrador y umbral se eligen con 4/5 y el costo se mide en el 1/5 que no se vio. Promedio de 20 particiones.
  - Umbral teórico 3/33 ≈ 0.09. ECE con 10 contenedores e IC 95 % por bootstrap.
- **Red densa (entregado):**

| Calibración | ECE | Brier | Honesto, umbral barrido | Honesto, umbral 0.09 |
|---|---|---|---|---|
| Sin calibrar | 0.099 [0.072, 0.148] | 0.108 | 919 ± 22 | **810** (54 FP, 0 FN) |
| Platt | **0.059** [0.046, 0.114] | 0.101 | 964 ± 110 | 833 (44.5 FP, 1.1 FN) |
| Isotónica | 0.086 [0.053, 0.130] | 0.103 | 902 ± 55 | 876 (41.4 FP, 1.7 FN) |

- **Lectura:**
  - **El costo honesto es más alto que el de T7.** 675 era optimista porque el umbral se elegía donde se medía; la cifra honesta está entre 810 y 960. Sigue siendo entre 2.3 y 2.8 veces menos que el mejor baseline (2,235).
  - **El umbral teórico le gana al barrido en todos los casos.** Con unos 160 casos para elegir, el barrido se sobreajusta.
  - **Platt mejora la calibración pero no el costo.** El ECE baja de 0.099 a 0.059 y el costo cambia de 810 a 833; la diferencia de +23 equivale a 1.5 FP por cada 200 reseñas, dentro del ruido. Con Platt, el mínimo de la curva de costo cae justo en 0.09 (`t9_barrido.png`).
  - **Respuesta a "¿decidir u ordenar?":** después de Platt, la probabilidad sirve para decidir, porque el umbral teórico es el de menor costo. Sin calibrar, el 0.09 funciona por coincidencia y el número que se mostraría no es una probabilidad fiable (ECE 0.099).
- **Referencia, logística:** su costo honesto es más bajo, de 518 a 575 (isotónica con 0.09: 518; Platt con barrido: 556), por unos 10 FP menos cada 200. Se reporta en el PDF. No se entrega porque el enunciado pide capas densas (brecha 16 de `PLAN.md`).
- **Pendiente (decisión del usuario):** qué calibración y umbral se congelan para la red densa.

## D27 · LSTM con embeddings propios (T8): descartada — 24-nov-2026

- **Hecho:** embeddings de 64 dimensiones entrenados desde cero (vocabulario del entrenamiento con frecuencia ≥ 2) y una capa LSTM con promedio de salidas, hasta 200 tokens. 4 combinaciones elegidas con validación cruzada en entrenamiento: gana 64 ocultas y dropout 0.5.
- **Cifras:**
  - AUC en validación cruzada de entrenamiento 0.810, contra 0.918 de la densa. AUC en validación 0.851, contra 0.928.
  - Costo honesto entre 1,269 y 1,411 min/1000, contra 810–964 de la densa. Con Platt el ECE baja a 0.028, pero ordena peor.
  - 45 s de cómputo.
- **Decisión:** se descarta. Con 300 ejemplos, una secuencia aprendida desde cero no alcanza a los n-gramas de TF-IDF.
- **Cómputo total de T7 + T8:** 70 s; T9: 8 s.

## D28 · Modelo congelado — punto de control B — 24-nov-2026

- **Elección del usuario (D26, opción A):** red densa sobre TF-IDF (128 ocultas, dropout 0.5, weight decay 1e-4), **calibrada con Platt** ajustado con las 200 de validación (a = 0.780, b = −0.817) y **umbral teórico 3/33 = 0.0909**.
  - Costo honesto esperado: 833 min/1000 (44.5 FP, 1.1 FN cada 200).
  - En validación, en la misma muestra del ajuste: 51 VP, 45 FP, 0 FN, 104 VN, costo 675, ECE 0.055, AUC 0.928.
- **Descartada:** sin calibrar con 0.09 (opción B, 810). El número que mostraría la app no sería una probabilidad fiable (ECE 0.099).
- **Filtro de fuera de dominio (ADR-05):** ajustado con las 1,323 reseñas aptas del periodo de entrenamiento. Pide que al menos el 50 % de las palabras sean comunes (top 300) y al menos el 62 % estén en el vocabulario del TF-IDF. En validación rechaza 2 de 200 reseñas reales (las dos `no_atender`), cerca del 1 % esperado por usar el percentil 1.
- **Reproducibilidad:** `scripts/congelar.py` reentrena con los hiperparámetros de T7 y reproduce las probabilidades evaluadas (diferencia máxima 5e-5). El `Predictor` cargado desde disco da las mismas probabilidades que el modelo en memoria. Latencia con el modelo cargado: mediana 0.9 ms, p95 1.6 ms.
- **Privacidad del modelo versionado:** antes de guardar se borra `stop_words_` del vectorizador, porque scikit-learn ahí guarda todos los n-gramas raros (frases y nombres). Además `vocabulary_` se reordena alfabéticamente: en su orden original las palabras seguían el orden del texto y la auditoría encontró 2 reseñas reconstruibles en 40 caracteres o más. Cada término conserva su índice, así que la red no cambia (`red.pt` quedó idéntico). La auditoría revisa ahora el vocabulario de los `.joblib`.
- **Cambio de código sin efecto en el modelo:** `limpiar` recorta a 5,000 caracteres en el último espacio para no partir una palabra. Ninguna reseña real pasa de 3,994 caracteres.
- **Artefactos:** `modelos/` (7.6 MB, ahora en git) con `MANIFIESTO.sha256`. `config.json` guarda los hashes de `resenas.csv`, `muestra.csv`, `muestra_prueba.csv` y `etiquetas.csv`.

### Protocolo de la corrida única sobre prueba (T12), fijado antes de verla

1. `evaluar_prueba.py` se niega a correr si: algún hash de `modelos/` no coincide con el manifiesto; los hashes de datos no coinciden con `config.json`; hay cambios sin commit en `src/`, `modelos/` o `scripts/evaluar_prueba.py`; o ya existe `resultados/prueba/`.
2. **Métrica principal:** el clasificador sobre las 200 de prueba, sin filtro. Se reportan la matriz de confusión con el umbral congelado, el costo por 1000, el AUC, el ECE con su curva de fiabilidad y el IC 95 % por bootstrap del costo y del ECE. También el costo de los tres baselines en prueba.
3. **Métrica secundaria:** el sistema completo con filtro. Una reseña rechazada cuenta como enviada al gerente, porque la app le pide a una persona que la revise.
4. **Las probabilidades se guardan por id, sin texto**, para T13 (errores).
5. Commit inmediato de `resultados/prueba/`. Si después aparece un error, no se borra nada: se agrega `resultados/prueba_corregida/` y una entrada aquí, y en el PDF van las dos cifras.

## D29 · Resultado de la corrida única sobre prueba (T12) — 24-nov-2026

- **Corrida:** `evaluar_prueba.py` en el commit `439f638`, con el modelo congelado en D28. Resultados en `resultados/prueba/`, commit `80c247d`, sin cambios posteriores. Antes, el candado se negó a correr mientras el script no estaba en un commit, y la segunda corrida con la sintética quedó bloqueada.
- **Prueba:** 200 reseñas, 42 `atender` (21 %; en validación 25.5 %).

| Modelo | Costo / 1000 | VP | FP | FN | VN |
|---|---|---|---|---|---|
| Nada es atender | 6,300 | 0 | 0 | 42 | 158 |
| Todo es atender | 2,370 | 42 | 158 | 0 | 0 |
| ≤ 2★ = atender (mejor baseline en prueba) | 2,115 | 29 | 11 | 13 | 147 |
| **Red densa + Platt, umbral 0.0909** | **750** [IC 95 %: 480, 1,140] | 41 | 40 | 1 | 118 |
| Sistema con filtro (6 rechazadas → gerente) | 810 | 41 | 44 | 1 | 114 |

- **Lectura:**
  - El costo es 2.8 veces menor que el del mejor baseline de prueba. En prueba ese baseline es el de estrellas (2,115), no "todo es atender" como en validación: con menos quejas (21 %), mandar todo cuesta más.
  - Atrapa 41 de 42 quejas y el gerente lee 81 de 200 reseñas (40 %).
  - Coincide con el costo honesto estimado en validación (833, D26), que cae dentro del IC.
  - AUC 0.947 (validación 0.928).
  - **Calibración:** ECE 0.023; la curva sigue a la diagonal en todos los contenedores. El IC por bootstrap [0.029, 0.076] no contiene el valor puntual porque el bootstrap sesga el ECE hacia arriba al repetir casos; se reporta así.
  - **Filtro:** rechazó 6 de 200 reseñas reales (3 %; en validación 1 %), 2 de ellas `atender`. Como una rechazada va al gerente, no agrega FN, pero suma 4 FP (+60 min/1000). Es una limitación del filtro que va a T14 y al PDF.
- **Errores para T13:** 41 (40 FP, 1 FN). Pasan de 20, así que no hace falta completar con validación (D8).

## D30 · Análisis de errores en prueba (T13) — 24-nov-2026

- **Hecho:** después de la corrida única y con permiso del usuario, Claude leyó las 41 reseñas mal clasificadas (40 FP, 1 FN) y las agrupó por tipo de falla, con una hipótesis de la causa. `resultados/prueba/errores_categorias.csv` (paráfrasis, sin texto) → `scripts/analizar_errores.py` → `resultados/prueba/errores.md`. **No se cambió ninguna etiqueta ni ningún resultado.**
- **Grupos (los 41 errores; entre paréntesis, cuántos entran en los 20):**
  - A. Etiqueta probablemente equivocada según la guía: el modelo marca una falla que la etiqueta no marcó (sobre todo lentitud o trato, R3). 12 (7)
  - B. Casos en la frontera de la guía: sabor contra falla, política contra cobro. 7 (4)
  - C. Decepción de sabor o precio leída como problema. 2 (2)
  - D. Reseña positiva o neutral con vocabulario de problemas (fila, espera, logística, ironía, faltas de ortografía). 10 (4)
  - E. Elogio apenas sobre el umbral bajo (p entre 0.09 y 0.19): es el costo aceptado de un umbral de 0.09. 9 (2)
  - F. El único FN: queja corta redactada con negaciones (p = 0.018). 1 (1)
- **Hallazgo principal:** 12 de los 40 FP (30 %) parecen errores de la etiqueta, no del modelo. Es coherente con la velocidad del etiquetado (D22): la consistencia (κ 0.72, D24) mide si la etiquetadora se repite a sí misma, no si se le escapa sistemáticamente un tipo de queja.
  - Consecuencias: el costo de prueba (750) probablemente es **pesimista**. Puede haber errores ocultos del otro lado: reseñas que la etiqueta y el modelo marcan igual de mal, y que este análisis no ve. Las etiquetas de entrenamiento probablemente tienen el mismo ruido.
  - El juicio del grupo A es de Claude aplicando la guía; **la etiquetadora debe confirmarlo antes de citarlo en el PDF**.
  - No se re-etiqueta ni se recalcula la prueba: el protocolo (D28) sólo permite una corrección declarada aparte.
- **Privacidad:** en 2 reseñas de prueba aparecieron 3 nombres que no se marcaron al etiquetar. Se agregaron a `data/nombres_escapados.txt` (fuera de git) para que la auditoría los detecte. No se volvió a correr `anonimizar.py`, porque cambiaría los hashes de datos después de la corrida única. No están en ningún archivo versionado.

## D31 · App (T10) — 24-nov-2026

- **Hecho:** `app/app.py` con Gradio 6.32.0 (agregado al `.venv`) sobre el mismo `Predictor` de la prueba.
  - Muestra la clase en palabras, la probabilidad calibrada, el umbral aplicado (9.1 %), una barra con la marca del umbral, una explicación y el tiempo. Si el filtro rechaza, dice "Fuera de dominio", da la razón y sugiere que la revise una persona.
  - Los ejemplos son inventados.
  - La telemetría de Gradio está desactivada, `share=False`, y no se guarda ni se registra lo que se escribe.
- **Verificado:**
  - La app levantada responde HTTP 200 a los 5 s.
  - Por la API del servidor, la primera predicción tarda 541 ms (calentamiento) y las siguientes unos 55 ms.
  - `tests/test_app.py`: 11 entradas raras sin excepción y sin inyectar HTML (el texto se escapa); p95 < 200 ms en 100 casos.
- **Descartadas:** Streamlit y FastAPI con HTML propio (ADR-07).

## D32 · 10 entradas fuera de dominio (T14) — 24-nov-2026

- **Hecho:** `scripts/probar_fuera_dominio.py` corre 10 entradas inventadas de tipos distintos (D9). Lo que debería responder la app en cada caso se escribió antes de correrlo. Resultado en `resultados/fuera_dominio/`.
- **Resultado:** 9 de 10 coinciden.
  - Se rechazan: vacía, sólo emojis, galimatías, inglés, portugués (38 % de palabras comunes contra un mínimo de 50 %), URL con números, HTML y la reseña de hotel. La de hotel apenas: 57 % de vocabulario contra un mínimo de 62 %.
  - La reseña de 11,730 caracteres se clasifica con aviso de recorte, como se esperaba.
  - **Falla:** una reseña de producto en español (celular roto) pasa el filtro y sale `atender` (p = 0.40). Es el límite previsto en ADR-05: el filtro mira idioma y vocabulario, no el tema. Lo correcto sería "fuera de dominio".
- **Reales no aptas (D9):** las 18 reseñas vacías y las 3 en otro idioma se rechazan.
- **Para el PDF ("cuándo no usar la app"):** sólo sirve para reseñas de restaurantes en español. Una queja en español sobre otro tipo de negocio se clasifica como si fuera de restaurante.

## D33 · Distribución: Space público de Hugging Face + Docker de respaldo — 24-nov-2026 (reemplaza a D16)

- **Decisión del usuario:** la forma principal de uso es una liga pública a un Space de Hugging Face (plan gratuito de CPU). El contenedor Docker que se construye desde el repo (T11) queda como respaldo reproducible. Todavía no se publica.
- **Razón:** la rúbrica pide que alguien la use sin que la autora esté presente y que no dependa de su máquina. Abrir una liga no requiere instalar nada; Docker garantiza que se pueda levantar aunque el Space falle.
- **Descartadas:**
  - Sólo Docker (D16): obliga a quien prueba a instalar Docker Desktop.
  - Space privado: quien prueba necesita cuenta de Hugging Face con acceso.
  - Liga temporal de Gradio: depende de la Mac encendida y caduca.
- **Consecuencias que se aceptan:**
  - El código de la app y `modelos/` quedan públicos. El vocabulario del modelo son palabras y n-gramas sueltos en orden alfabético, sin `stop_words_` (D28); no hay reseñas, datos ni la key.
  - Lo que escribe quien la usa se procesa en servidores de Hugging Face. La app no lo guarda.
  - El Space se duerme tras 48 h sin uso; hay que abrirlo antes de grabar o de compartir la liga.

## D34 · Preparación del Space y del contenedor (sin publicar) — 24-nov-2026

- **Hecho:**
  - **Contenedor único:** `Dockerfile` (python 3.12.13-slim, uv 0.12.1, usuario 1000, torch CPU), `.dockerignore` en lista blanca, `compose.yaml` con healthcheck y `space/README.md` (tarjeta del Space, `sdk: docker`).
  - **`scripts/preparar_space.py`** arma `dist/space/`, que no se versiona: 27 archivos, 7.8 MB, sólo `src/resenas/`, `app/`, `modelos/`, `pyproject.toml`, `uv.lock`, `Dockerfile` y la tarjeta. Verifica el manifiesto, rechaza rutas prohibidas y corre `auditar_seguridad.py --carpeta`. Resultado: sin hallazgos.
  - **spaCy pasa al grupo de dependencias `datos`:** se instala en local por omisión (`default-groups`), pero no en el contenedor (`--no-default-groups`).
  - **`RESENAS_RAIZ`** permite indicar la raíz del proyecto en el contenedor. Sólo cambia rutas: el predictor da las mismas probabilidades (`app/referencia.json`, 12 textos inventados, 12/12 iguales).
  - La app avisa que no se escriban datos personales y que el texto no se guarda.
- **Sesión de Hugging Face:** iniciada por el usuario con el CLI. El token queda fuera del repo.
- **Regla:** no se crea ni se sube el Space sin autorización explícita del usuario.
- **Falta:** construir y probar el contenedor en local (Docker Desktop no estaba corriendo).

## D35 · Nuevo diseño de la app (propuesta de Stitch) — 24-nov-2026

- **Hecho:** el usuario generó un diseño con Stitch a partir de una descripción del proyecto. Se adaptó a Gradio: `app/estilo.css`, más la estructura de `app/app.py`.
  - Dos paneles: texto con ejemplos, y dictamen del modelo.
  - Tarjetas para los estados atender, no atender, fuera de dominio y vacío. Muestran la probabilidad y el umbral en grande, y una barra con la marca del umbral.
  - Modo claro y oscuro; en móvil los paneles se apilan.
- **De Stitch NO se usó:**
  - Su JavaScript, que traía un "motor de clasificación simulado": palabras clave y probabilidades con `Math.random()`. Usarlo habría mostrado resultados falsos.
  - Textos que afirmaban cosas que el modelo no hace: el tipo de problema, "idioma detectado", "umbral óptimo", "alucinaciones".
  - Etiquetas fijas en los ejemplos: ahora las calcula el modelo al arrancar.
  - **Todos los números siguen saliendo del `Predictor` congelado.**
- **Verificado:**
  - Capturas con Playwright y Chromium temporales (vía `uvx`, no se agregaron al proyecto) en escritorio, móvil (390 px) y modo oscuro, en `docs/capturas/`.
  - Por el servidor, las 12 respuestas coinciden con `app/referencia.json`.
  - 95 pruebas pasan; el texto del usuario se escapa y nunca se inyecta como HTML.
- **Nota:** las fuentes Inter y JetBrains Mono se cargan desde Google Fonts en el navegador de quien usa la app. Si no cargan, se usan las del sistema.

## D36 · Buscador de restaurantes con Google Maps: descartado — 24-nov-2026

- **Decisión del usuario:** no se agrega a la app un buscador que traiga las reseñas de un restaurante desde Google Maps y las clasifique.
- **Razón:** no lo pide la rúbrica ("un archivo o un texto"); trae sólo 5 reseñas por lugar; exige una key en el Space con riesgo de cobro (se habría controlado con cuota diaria en GCP, límites por sesión e interruptor de apagado) y atribución de autores según los términos de Google; y cuesta de medio día a un día de trabajo a 6 días de la entrega.
- **Descartada:** hacerlo como pestaña opcional, apagada por omisión. Se dejaría para un trabajo futuro y se menciona así en el PDF.

## D37 · Rediseño de la app como editor de documentos — 24-nov-2026

- **Decisión del usuario:** cambiar el diseño de D35 por uno tipo editor de documentos, tomando como referencia la distribución de un editor comercial (captura que dio el usuario).
- **Qué se tomó:** hoja grande con el texto sin bordes; barra superior con palabras, caracteres e idioma; panel derecho con secciones en tarjeta (dictamen con la probabilidad grande y una leyenda de umbral, decisión y tiempo; ejemplos); aviso al pie del panel; píldora flotante Borrar / Analizar.
- **Qué no se tomó:** promociones, menú de herramientas, cuenta, deshacer/rehacer, barra de íconos, ni el nombre, logo o colores de la marca de referencia. Colores propios (azul `#2f5bd3`); modo oscuro y móvil (el panel pasa debajo del editor a menos de 900 px).
- **Cambio de contrato:** la tarjeta de resultado lleva `data-clase` y `data-probabilidad` (4 decimales); `referencia_app.py --url` las lee en lugar de buscar texto visible, así el diseño puede cambiar sin romper la verificación.
- **Sin cambios en el modelo ni en el `Predictor`.** Verificado: 95 pruebas, 12/12 contra `app/referencia.json` local y por el servidor; capturas nuevas en `docs/capturas/`.
- **Descartada:** quedarse con el diseño de D35 (al usuario no le terminó de convencer).

## D38 · Botones Borrar / Analizar siempre visibles — 24-nov-2026

- **Pedido del usuario:** la píldora de acciones debe estar en pantalla en todo momento, como en la referencia de D37; con reseñas largas quedaba al fondo del editor y había que bajar.
- **Cambio (sólo CSS):** en escritorio la píldora es `sticky` al borde inferior de la pantalla mientras el editor esté a la vista; en pantallas de menos de 900 px es `fixed` abajo al centro. Gradio pone `overflow: hidden` en su contenedor, que impide el sticky; se cambió a `overflow: clip`.
- **Verificado con Playwright** (reseña de 2,475 caracteres): el botón Analizar está visible en 3 posiciones de scroll en escritorio (1280×720) y en móvil (390×844), y funciona al hacer clic; la página no se desborda a lo ancho ni con 6,000 caracteres.
- **Descartada:** `fixed` también en escritorio, porque quedaría centrada en la ventana y no en el editor.

## D39 · Publicación en Render en lugar del Space de Hugging Face — 24-nov-2026

- **Qué pasó:** con la autorización del usuario se intentó crear el Space `Manu-se/atender-resenas`. Hugging Face respondió 402: hoy los Spaces de Docker y de Gradio en CPU gratuita piden suscripción PRO, y gratis sólo quedan los estáticos. No se creó ni se subió nada.
- **Decisión del usuario:** publicar el mismo contenedor en Render, en el plan gratuito (512 MB de RAM; la app usa unos 350 MB en el contenedor local). Reemplaza el destino de D33/D34; el Dockerfile no cambia.
- **Cómo:** `render.yaml` en la raíz define un servicio web Docker (`atender-resenas`, plan free, chequeo de salud en `/`, sin despliegue automático). Render construye desde el repo privado de GitHub; el `.dockerignore` de lista blanca deja fuera `data/`, `resultados/`, `.env` y `cache/`.
- **Costo aceptado:** el servicio se duerme tras 15 min sin uso y el primer acceso tarda alrededor de 1 min. Para el video se abre antes de grabar.
- **Descartadas:** pagar HF PRO (alrededor de 9 USD al mes); un Space estático con la inferencia reescrita en numpy para el navegador (medio día o más y riesgo de diferencias numéricas); no publicar.

## D40 · Endurecimiento antes de publicar (auditoría del 24-nov) — 24-nov-2026

- **Auditoría completa antes del push** (pedido del usuario):
  - `auditar_seguridad.py --historial` y gitleaks 8.21.2 sobre los 25 commits: sin hallazgos.
  - Nunca entraron al historial `.env`, `data/` real, `cache/` ni llaves. El único correo en los metadatos es el noreply de GitHub.
  - pip-audit sobre las 72 dependencias de ejecución: sin vulnerabilidades conocidas.
  - El contenedor no sirve `modelos/` ni el código (403/404) y corre sin root.
- **Tres cambios de endurecimiento; ninguno cambia predicciones (12/12 contra `app/referencia.json`, local y en el contenedor):**
  1. **El `Predictor` verifica `MANIFIESTO.sha256` antes de cargar** (`verificar_manifiesto`). `vectorizador.joblib` es un pickle, que puede ejecutar código si alguien lo cambia. Si falta el manifiesto o un archivo no coincide, lanza `ManifiestoInvalido` y no carga nada. Toca `predictor.py`: por eso esta entrada (regla de D28). Los pesos y los hashes de `modelos/` no cambian.
  2. **Tope de entrada de 20,000 caracteres** (`max_length` en la caja y recorte en el servidor, para llamadas directas a la API). Sólo se analizan los primeros 5,000, como antes. Protege la RAM de 512 MB del plan gratuito.
  3. **Cola acotada:** `queue(max_size=20)`. Las peticiones de más se rechazan en lugar de amontonarse.
- **Pruebas nuevas:** se niega sin manifiesto y con un byte de más en el vectorizador; el modelo congelado real pasa el manifiesto; entrada de 200,000 caracteres topada en el servidor. 98 pruebas pasan.
- **Descartadas:**
  - Límite de peticiones por IP: Gradio no lo trae y un proxy propio es más trabajo del que vale para una práctica sin costo por uso.
  - Firmar el modelo con llave: el manifiesto en git ya fija los hashes.
