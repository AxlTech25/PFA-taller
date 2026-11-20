[← Volver al README principal](../../../README.md)

# Evaluación de usabilidad (SUS)

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.

**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth

**Sprint:** 4 (`ECO Sprint 4`, 30/10/2026 – 12/11/2026). Versión: 1.0.0.

**Instrumento:** System Usability Scale (SUS), 10 ítems, formulario [Evaluación de usabilidad – EcoLogística Lima](https://forms.gle/4pUiEtxLqffGGF2y7).

**Aplicación:** 20/11/2026, 14:33–15:35 (America/Lima), sobre [https://ecologistica-lima-beige.vercel.app](https://ecologistica-lima-beige.vercel.app). La API de ese sitio está en Railway.

**Muestra:** n = 7. Las siete personas marcaron el rol Estudiante y respondieron Sí a haber completado todas las tareas.

Las respuestas anonimizadas están en [sus/respuestas.csv](./sus/respuestas.csv). Ninguna cifra de este informe se redondeó de nuevo: se archivan tal como quedaron calculadas.

---

## 1. Ítems y puntuación

La escala de cada ítem es 1 = Totalmente en desacuerdo, 5 = Totalmente de acuerdo. El orden es el estándar. Los ítems impares están redactados en positivo y los pares en negativo.

| # | Ítem en el formulario | Polaridad |
|---:|---|---|
| 1 | Creo que me gustaría usar este sistema con frecuencia. | Positiva |
| 2 | Encontré el sistema innecesariamente complejo. | Negativa |
| 3 | Pensé que el sistema era fácil de usar. | Positiva |
| 4 | Creo que necesitaría el apoyo de un técnico para poder usar este sistema. | Negativa |
| 5 | Encontré que las diversas funciones del sistema estaban bien integradas. | Positiva |
| 6 | Pensé que había demasiada inconsistencia en el sistema. | Negativa |
| 7 | Imagino que la mayoría de las personas aprendería a usar este sistema muy rápidamente. | Positiva |
| 8 | Encontré el sistema muy complicado de usar. | Negativa |
| 9 | Me sentí muy seguro(a) usando el sistema. | Positiva |
| 10 | Necesité aprender muchas cosas antes de poder empezar a usar este sistema. | Negativa |

Los ítems 4, 8 y 9 conservan la polaridad estándar y cambian un poco la redacción más citada en español: el 4 dice «un técnico» (no «una persona técnica»), el 8 dice «complicado» (no «engorroso») y el 9 dice «seguro(a)».

Puntuación de Brooke: en cada ítem impar, contribución = respuesta − 1; en cada ítem par, contribución = 5 − respuesta. Cada contribución queda entre 0 y 4. La suma de las diez contribuciones se multiplica por 2,5 y el SUS queda entre 0 y 100. El umbral de referencia es 68.

Dos lecturas de la misma nota, sin cambiar el número:

| Escala | Cortes usados en esta acta |
|---|---|
| Sauro–Lewis (curva) | A+ 84.1–100; A 80.8–84.0; A− 78.9–80.7; B+ 77.2–78.8; B 74.1–77.1; B− 72.6–74.0; C+ 71.1–72.5; C 65.0–71.0; C− 62.7–64.9; D 51.7–62.6; F 0–51.6 |
| A–F simple | A 90.0–100; B 80.0–89.9; C 70.0–79.9; D 60.0–69.9; F 0–59.9 |

La letra Sauro–Lewis de 80,0 es A− (el corte A empieza en 80,8). La letra simple de 80,0 es B. 72,5 cae en C+ de Sauro–Lewis y en C simple.

## 2. Puntajes individuales

| Participante | Q1–Q10 | SUS | Sauro–Lewis | Simple |
|---|---|---:|---|---|
| P1 | 4, 4, 4, 3, 4, 2, 3, 2, 3, 3 | 60.0 | D | D |
| P2 | 4, 3, 4, 2, 4, 2, 4, 1, 5, 1 | 80.0 | A− | B |
| P3 | 4, 5, 4, 5, 5, 5, 4, 5, 5, 5 | 42.5 | F | F |
| P4 | 4, 5, 4, 4, 5, 4, 4, 5, 4, 5 | 45.0 | F | F |
| P5 | 5, 1, 3, 2, 5, 1, 4, 2, 4, 3 | 80.0 | A− | B |
| P6 | 4, 4, 5, 4, 4, 4, 3, 5, 4, 5 | 45.0 | F | F |
| P7 | 4, 2, 4, 3, 4, 2, 4, 2, 4, 2 | 72.5 | C+ | C |

| Estadístico | Valor |
|---|---:|
| n | 7 |
| Media | 60.71 |
| Mediana | 60.0 |
| Desviación estándar muestral | 16.88 |
| Mínimo | 42.5 |
| Máximo | 80.0 |
| Personas con SUS ≥ 68 | 3/7 |

La media 60.71 queda en D en las dos escalas y por debajo del umbral 68. Ese es el resultado oficial de esta aplicación.

## 3. Ítem por ítem

La contribución es la media ya convertida a la escala 0–4. La media cruda es la respuesta 1–5, antes de invertir los ítems pares.

| Ítem | Contribución media (0–4) | Media cruda (1–5) |
|---:|---:|---:|
| Q1 | 3.14 | 4.14 |
| Q2 | 1.57 | 3.43 |
| Q3 | 3.00 | 4.00 |
| Q4 | 1.71 | 3.29 |
| Q5 | 3.43 | 4.43 |
| Q6 | 2.14 | 2.86 |
| Q7 | 2.71 | 3.71 |
| Q8 | 1.86 | 3.14 |
| Q9 | 3.14 | 4.14 |
| Q10 | 1.57 | 3.43 |

Las contribuciones más bajas son las de los ítems negativos: Q2 1.57, Q10 1.57, Q4 1.71 y Q8 1.86. En bruto, esas mismas respuestas siguen altas (3.43, 3.43, 3.29 y 3.14): mucha gente marcó acuerdo también donde el ítem describe un problema.

## 4. Aquiescencia y nota exploratoria

P3 y P4 marcaron 4 o 5 en los diez ítems. P6 marcó 4 o 5 en nueve; Q7 quedó en 3. En los tres casos, los cinco ítems pares (los negativos) están en 4 o 5. En P3 esos cinco pares valen 5, así que su contribución par es 0 y el SUS baja a 42.5 aunque el comentario es favorable («La interacción y la usabilidad» / «El diseño un poquito»). P4 y P6 también escriben comentarios positivos. La lectura más directa es aquiescencia, o que no se leyó la polaridad de los ítems pares. Los puntajes se archivan como se respondieron. No se corrigen.

Si se dejan fuera P3, P4 y P6, quedan P1, P2, P5 y P7 (60.0, 80.0, 80.0 y 72.5) y la media es 73.1. Esa cifra es exploratoria. No sustituye a la media oficial de 60.71 ni al grado D.

## 5. Comentarios abiertos

| Participante | Qué gustó | Qué mejoraría |
|---|---|---|
| P1 | El facil uso y la facilidad | solo el aspecto |
| P2 | El diseño de las interfaces y lo fácil que fue navegar en el sistema | Mejoraría algunos botones |
| P3 | La interacción y la usabilidad | El diseño un poquito |
| P4 | Fue creativo | Creo que esta perfecto |
| P5 | Me gustó la interfaz | Nada |
| P6 | La interfaz | La manera de iniciar sesion |
| P7 | La interfaz | La estructura |

## 6. Límites de la muestra

Las siete personas son estudiantes. No hay Operador logístico, Gerente ni otro rol de DistriRápido. n = 7 es una muestra pequeña: la desviación estándar muestral es 16.88 y tres personas quedan en F por el patrón de la sección 4. El resultado no se puede leer como la usabilidad para quien opera la consola en el trabajo.

## 7. Qué cambiar y cómo volver a medir

Los comentarios que piden un cambio, sin reinterpretar los que dicen que no cambiarían nada (P4 y P5), apuntan a cuatro cosas: el aspecto visual, algunos botones, la manera de iniciar sesión y la estructura de la navegación.

La siguiente pasada tiene que avisar, antes de responder, que los ítems pares están en negativo, o usar una versión del SUS en la que todos los ítems vayan en la misma dirección. Y tiene que incluir a personas con el rol de operación o de gerencia, no solo a estudiantes. Hasta esa pasada, el resultado de esta acta sigue siendo 60.71, grado D, por debajo de 68.

---

## Historial de Control de Cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 20/11/2026 | Equipo EcoLogística Lima | Primera acta SUS. n = 7, estudiantes, 20/11/2026 14:33–15:35 (Lima), sitio público. Media 60.71, grado D, 3/7 en o sobre 68. La media 73.1 sin P3, P4 y P6 queda marcada como exploratoria. |

[← Volver al README principal](../../../README.md)
