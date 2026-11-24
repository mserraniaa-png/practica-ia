| # | Tipo | Entrada (inventada) | Responde la app | Razón o aviso | Debería | ¿Coincide? |
|---|---|---|---|---|---|---|
| 1 | Vacía | `` | fuera de dominio | Vacía: no hay texto que analizar. | fuera de dominio | ✔ |
| 2 | Sólo emojis | `😋🔥👍👍🌮` | fuera de dominio | Muy corta: tiene 0 palabra(s); se necesitan al menos 3. | fuera de dominio | ✔ |
| 3 | Galimatías | `asdkj qwpoe zmxn alskdj qpwoei lkjhg` | fuera de dominio | No parece una reseña en español: sólo 0% de sus palabras son palabras comunes de las reseñas (mínimo 50%). | fuera de dominio | ✔ |
| 4 | Reseña en inglés | `The tacos were amazing but the waiter forgot our drinks twice.` | fuera de dominio | No parece una reseña en español: sólo 9% de sus palabras son palabras comunes de las reseñas (mínimo 50%). | fuera de dominio | ✔ |
| 5 | Reseña en portugués | `A comida estava ótima, mas o garçom demorou muito para trazer a conta.` | fuera de dominio | No parece una reseña en español: sólo 38% de sus palabras son palabras comunes de las reseñas (mínimo 50%). | fuera de dominio | ✔ |
| 6 | Reseña de hotel (español) | `La habitación estaba sucia, las toallas olían mal y el aire acondicionado no servía.` | fuera de dominio | Vocabulario desconocido: sólo 57% de sus palabras las conoce el modelo (mínimo 62%). | fuera de dominio | ✔ |
| 7 | Reseña de producto (español) | `El celular llegó con la pantalla rota y la batería dura muy poco.` | atender (p = 0.40) |  | fuera de dominio | ✘ |
| 8 | URL y números | `https://www.ejemplo.com 5555 1234 99` | fuera de dominio | Vocabulario desconocido: sólo 0% de sus palabras las conoce el modelo (mínimo 62%). | fuera de dominio | ✔ |
| 9 | HTML / código | `&lt;div>&lt;script>alert('hola')&lt;/script>&lt;/div>` | fuera de dominio | No parece una reseña en español: sólo 0% de sus palabras son palabras comunes de las reseñas (mínimo 50%). | fuera de dominio | ✔ |
| 10 | Reseña de restaurante muy larga (11,730 caracteres) | `La comida estuvo rica pero el mesero tardó mucho en traer la cuenta. La comida e… (11,730 caracteres)` | atender (p = 0.52) | Texto de 11,730 caracteres: se analizaron los primeros 5,000. | clasificar normal (con aviso) | ✔ |

Reseñas reales no aptas (D9): vacías 18/18 rechazadas; en otro idioma 3/3 rechazadas.
