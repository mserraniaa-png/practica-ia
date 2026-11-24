# Guía de etiquetado

Versión 1 · **aprobada por la etiquetadora el 24-nov-2026**, antes de etiquetar la primera reseña (T1, D19).

Pregunta: **¿esta reseña reporta un problema concreto que el negocio puede corregir?**

| Tecla | Etiqueta | Cuándo |
|---|---|---|
| `1` | `atender` | Reporta al menos un problema concreto y corregible, aunque la reseña sea positiva o el problema se haya resuelto |
| `0` | `no_atender` | Elogio, opinión de gusto, queja vaga, sugerencia, comentario neutro o información |
| `s` | ambigua | Después de aplicar esta guía sigue sin poder decidirse (ver §4) |
| `n` | (marca) | Hay un nombre de persona que la anonimización dejó pasar (ver §5). Se marca y además se etiqueta |

Reglas generales:
- **Las estrellas no deciden** (por eso la herramienta no las muestra).
- **Basta un problema.** Si la reseña tiene varios temas y uno solo es un problema concreto, es `1`.
- Se juzga lo que dice el texto, no lo que uno supone que pasó.
- Se lee la reseña completa. Si es muy larga, se busca el problema, no la impresión general.

Los ejemplos son reseñas reales **que no están en la muestra ni son del periodo de prueba**, así que ninguna etiqueta de la muestra viene de esta guía. Se citan por `id` con una paráfrasis corta; el texto completo está en `data/resenas.csv`, que no se versiona.

## 1. Casos de D11

### 1.1 Problema que se resolvió en el momento → `1`

La falla ocurrió y puede repetirse; la etiqueta es "reporta un problema", no "sigue sin resolverse".

| id | Paráfrasis | Etiqueta |
|---|---|---|
| `8618c23f957c` | Los camarones del platillo llegaron congelados por dentro; al decirlo, se lo cambiaron amablemente | `1` |
| `fc6a9210ab9e` | La atención fue excelente, pero tres caldos venían tan salados que no se podían comer; el personal ofreció cambiarlos | `1` (ver R1: incomible no es cuestión de gusto) |

### 1.2 Precio → `0`, salvo error de cobro → `1`

Opinar que algo es caro es gusto. Un error de cobro (cobrar de más, cobrar algo no servido, propina o comisión forzada, precio distinto al anunciado) es una falla.

| id | Paráfrasis | Etiqueta |
|---|---|---|
| `2948ca0d388b` | Hamburguesas ricas, pero el precio es algo elevado | `0` |
| `234bec8a0bdc` | Muy caro para lo poco que dan: $90 por una torta pequeña | `0` |
| `2be10999b5e2` | La cuenta debía ser $250 y les cobraron $295 | `1` |
| `5aec52123023` | Cobran comisión por pagar con tarjeta | `1` |
| `946799f6991b` | Afuera anuncian un precio y luego cobran todo aparte (además, tardan mucho en atender) | `1` |

### 1.3 Queja vaga → `0`

No le da al gerente nada que corregir.

| id | Paráfrasis | Etiqueta |
|---|---|---|
| `a70778c62afb` | Los chilaquiles son muy básicos, dejan mucho que desear; debió pedir otra cosa | `0` |
| `024a805ecf13` | En general bien para comer tacos, nada extraordinario | `0` |

### 1.4 Reseña positiva con un problema de pasada → `1`

Es justo el caso donde las estrellas fallan.

| id | Paráfrasis | Etiqueta |
|---|---|---|
| `a46e51fb04bb` | Hamburguesas muy ricas, muy recomendable; lo único malo, los refrescos estaban tibios | `1` |
| `0c3bacb97ccc` | Muy buen servicio y buen sándwich, pero la carta decía que traía papitas y no se las sirvieron | `1` |
| `4e04c646bb12` | Muy rico, pero tardaron en atender, no le pusieron cebolla a los chilaquiles y quien tomó la orden se distraía | `1` |

### 1.5 Sugerencia sin falla → `0`

| id | Paráfrasis | Etiqueta |
|---|---|---|
| `aaff666d3e47` | Le gusta la cafetería; pide que amplíen la carta de bebidas | `0` |
| `768c64c63b9a` | Quita una estrella sólo porque la música no le parece la adecuada | `0` |
| `181d879e1b98` | "Deberían dejar que se dore el pollo": lo dan medio crudo | `1`: está redactada como sugerencia, pero reporta una falla |

## 2. Reglas adicionales (aprobadas el 24-nov, D19)

### R1 · Sabor contra falla de preparación

- **Falla verificable → `1`:** crudo, frío cuando debía ir caliente, congelado, incomible de salado o quemado, en mal estado, cabello o insectos, platillo equivocado, ingrediente anunciado que faltó, porción menor a la anunciada.
- **Juicio de sabor → `0`:** sin sabor, desabrido, muy dulce, no me encantó, muy básico, el de otro lugar es mejor.

| id | Paráfrasis | Etiqueta |
|---|---|---|
| `8b0a1bfa8b6f` | La carne de la hamburguesa llegó cruda y fría, y tardaron en servirla | `1` |
| `47d88a77e8b2` | Al abrir el pollo para llevar en casa salieron cucarachas | `1` |
| `478b2cff9fa3` | El pulque no tiene sabor ni consistencia; los curados son licuados azucarados | `0` |
| `c1d87e660027` | La ensalada tenía demasiado aderezo y la pizza de hongos no le encantó | `0` |

### R2 · Características del local y políticas → `0`, salvo que causen una falla

Local pequeño, mesas juntas, sólo efectivo, sin estacionamiento, cierra temprano, cobran aparte algo que está anunciado: son condiciones conocidas, no fallas. Higiene, trato, tiempo, cobro y producto sí son fallas.

| id | Paráfrasis | Etiqueta |
|---|---|---|
| `29df96c7e72b` | Bueno y barato, informal; no aceptan tarjeta | `0` |
| `4a229768c9fa` | La calidad se mantiene; el único pero es que hay un solo baño y es pequeño | `0` |
| `d18c566af69a` | Tacos ricos, pero vio al taquero toser sobre los tacos al servir | `1` |

### R3 · Servicio y tiempo → `1` si hay un hecho

Trato grosero, espera concreta, mesero que desaparece, pedido equivocado: `1`. "El servicio es lento" también cuenta, porque el tiempo es corregible (D11).

| id | Paráfrasis | Etiqueta |
|---|---|---|
| `7bc5c394259c` | El pollo es bueno, pero se puede estar 10–15 minutos afuera y nadie atiende | `1` |
| `8d7cf1c5a379` | Vale la pena, pero el servicio es lento: tardan en traer la carta y en tomar la orden | `1` |

### R4 · Pedidos a domicilio o por aplicación → `1`

Si la falla es del negocio o de su entrega (llegó frío, crudo, incompleto, no surtieron el pedido), es `1` aunque intervenga una aplicación.

| id | Paráfrasis | Etiqueta |
|---|---|---|
| `de81d7458c74` | Pedido a domicilio: llegó frío y revuelto después de una hora | `1` |
| `991ba3cab1bb` | Sin conexión en el local, el pedido hecho por aplicación nunca se preparó | `1` |

### R5 · Negativa sin hechos pero que nombra un área → `1` (opción A, D19)

Ejemplo: `51385caeffae`, que califica de pésimas la comida, la higiene y el trato, sin contar qué pasó. No da un hecho, pero sí dice **dónde** está el problema (higiene, atención).

- **Opción A (elegida): `1`** si nombra un área corregible (higiene, trato, tiempo, cobro, estado de la comida) con un juicio negativo, aunque no dé detalles. Sólo es `0` cuando la queja es global ("mala experiencia", "no vuelvo").
- *Opción B (descartada): `0`.* Sin un hecho concreto, el gerente no tiene qué revisar.

`51385caeffae` → `1`. Sigue siendo `0` la queja global sin área: "mala experiencia", "no vuelvo", "pésimo lugar".

## 3. Orden de decisión

1. ¿Es una reseña de restaurante en español que se entiende? Si no → `s` (§4).
2. ¿Hay al menos un hecho que sea una falla de producto, higiene, trato, tiempo, cobro o entrega (R1–R4)? → `1`.
3. ¿Hay una queja negativa que nombra un área corregible, aunque sin hechos? → `1` (R5).
4. Lo demás (elogio, gusto, precio, queja global, sugerencia, característica del local, información) → `0`.

## 4. Ambiguas (`s`, D7)

Se usa `s` sólo si:
- el texto no se entiende, está cortado o casi todo está en otro idioma;
- no es una reseña de restaurante (otro negocio, spam, una pregunta);
- después de aplicar §3 sigue genuinamente empatada (una regla dice `1` y otra `0`).

No se usa `s` para evitar una decisión difícil que la guía sí resuelve. Las ambiguas se excluyen, se cuentan y se reemplazan con una reserva del mismo split (D7, D17); la herramienta lo hace sola.

## 5. Nombres que se escaparon (`n`, D10)

Se marca con `n` cualquier nombre de persona que siga visible: mesero, gerente, dueño, otro cliente. Pasa sobre todo en elogios ("nos atendió el mesero …"), con el nombre en minúsculas o entre paréntesis. No se marcan nombres de restaurantes, platillos, lugares ni de marcas. Antes de entrenar, los marcados se cambian por `[PERSONA]` (D10).

En las reseñas que se revisaron para esta guía aparecieron 4 nombres que se escaparon, todos de meseros en elogios (`9ff4b2a4373b`, `dd65f8cc28af`, `bc0523349bca`, `01373e358249`).

## 6. Cambios a la guía

Si durante el etiquetado aparece un caso que la guía no resuelve, se agrega aquí la regla nueva con fecha y desde qué reseña rige, y se anota en `DECISIONES.md`. **No se re-etiqueta en silencio:** si la regla nueva cambia etiquetas anteriores, se re-etiquetan con la herramienta (queda registrado) y se cuenta cuántas cambiaron.

| Fecha | Cambio | Desde |
|---|---|---|
| 23-nov | Versión 1 (borrador) | — |
| 24-nov | Aprobada: R1–R4 tal cual; R5 = opción A | Primera reseña |
