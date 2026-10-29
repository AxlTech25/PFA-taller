[← Volver al README Principal](../../../README.md)

# Retrospectiva del sprint

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.

**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth

## ¿Qué aprendimos?

- La primera pasada por SonarQube, la herramienta que revisa la calidad y la seguridad del código, nos mostró poca cobertura de pruebas: cerca del 53 %. También apareció un aviso de seguridad.
- No teníamos el programa de análisis instalado. Lo corrimos de otra forma, con Docker, que permite usar la herramienta sin instalarla en la computadora.
- Al principio el porcentaje de pruebas ni siquiera se veía bien. Tuvimos que cambiar cómo se arman y cómo se leen los reportes, tanto en la parte del servidor como en la de la pantalla.
- Para probar también chocamos con la base de datos de la computadora: ya había otra base usando el mismo puerto, así que usamos uno distinto.
- Corregimos lo que SonarQube marcó. Uno de los avisos era una contraseña de la base escrita en el código; la sacamos para que el programa la tome de la configuración. Escribimos muchas más pruebas y volvimos a correr el análisis varias veces, hasta que el control de calidad quedó aprobado, sin avisos pendientes. La cobertura subió a cerca del 97 %.
- Medir accesibilidad era nuevo para nosotros. Tuvimos que aprender a usar tres herramientas: axe DevTools, Lighthouse y WAVE. Abrimos la aplicación en la computadora, fuimos pantalla por pantalla, tomamos capturas, interpretamos los resultados y corregimos lo que marcaban.
- El porcentaje de cumplimiento lo calculamos a mano, principio por principio, como pide la plantilla: que se pueda percibir, usar, entender y que funcione con las ayudas de quien navega. Después de las correcciones, los puntos que aplican a nuestra aplicación quedaron cubiertos.
- En Lighthouse el celular salió más bajo que la computadora: 59 frente a 86. Esa medición se hizo con la aplicación en modo de desarrollo, no con la versión ya armada.

## ¿Qué estamos haciendo bien?

- No nos quedamos con el primer resultado. Corregimos los avisos, aumentamos las pruebas y repetimos el análisis hasta que pasó.
- Las pruebas cubren mucho más que al inicio, en el servidor y en la pantalla.
- En accesibilidad no miramos una sola pantalla. Recorrimos la aplicación, guardamos las capturas y corregimos lo que salió: el recuadro del teclado que no se veía, botones que se llamaban igual y el mapa sin un texto que lo explique.
- Dejamos escrito cómo repetir la medición, para que otro compañero no empiece de cero.

## ¿Qué podemos hacer mejor?

### Personas

- Era la primera vez del equipo con SonarQube y con las herramientas de accesibilidad. Aprender a usarlas nos quitó tiempo que no habíamos separado.
- Conviene explicar los hallazgos el mismo día y en palabras simples, para que no dependan solo de quien hizo la prueba.

### Relaciones

- Las capturas ayudaron a mostrar el resultado a quien no tenía la herramienta abierta.
- Calidad y accesibilidad hay que comentarlas en la reunión del sprint, no solo dejarlas en el documento. Así todo el equipo sabe qué se corrigió y qué sigue abierto.

### Procesos

- El primer análisis salió incompleto porque los reportes de cobertura no se leían bien. La próxima vez hay que generarlos bien antes de pasar SonarQube, no después de ver que el porcentaje no aparece.
- El control de calidad se hizo a mano, en una computadora, y hubo que repetirlo varias veces. Si no queda automático al subir cambios, se nos puede pasar un aviso.
- Dejamos sin actualizar unas librerías que siguen con avisos, para no romper lo que ya estaba probado. Fue una decisión del sprint y queda pendiente.

### Herramientas

- Sin el analizador instalado, Docker nos permitió avanzar. Igual dependemos de tener Docker listo y de repetir los pasos a mano.
- La base de pruebas no puede usar el puerto que ya ocupa otra base en la computadora. Hay que tener eso presente antes de correr las pruebas.
- axe DevTools, Lighthouse y WAVE no muestran lo mismo. Al principio costó saber qué mirar en cada una. Hay que pasar las tres y después interpretar.
- Lighthouse marcó 59 en el celular y 86 en la computadora, con la aplicación en desarrollo. Hay que volver a medir cuando esté armada para uso real.

### Acciones a realizar

- Actualizar las librerías de la interfaz que todavía tienen avisos de seguridad (son 9) y volver a revisarlas sin romper las pruebas. Dueño: equipo. Meta: el próximo sprint.
- Mejorar la velocidad en el celular. Hoy la medición es 59 en móvil y 86 en computadora, en modo de desarrollo. Medir de nuevo con la versión armada y corregir lo que siga lento. Dueño: equipo. Meta: el próximo sprint.
- Hacer que el control de calidad de SonarQube corra solo al subir cambios, y no solo a mano con Docker. Dueño: equipo. Meta: el próximo sprint.
- Anotar en pocas líneas cómo se generan los reportes de cobertura del servidor y de la pantalla, para que el primer análisis ya muestre el porcentaje. Dueño: equipo. Meta: al empezar el próximo sprint.
- Seguir midiendo accesibilidad con axe DevTools, Lighthouse y WAVE cuando cambiemos una pantalla, y calcular otra vez el porcentaje si el resultado cambia. Dueño: equipo. Meta: el próximo sprint.

El detalle de las mediciones está en los otros documentos de esta carpeta: [revisión](./01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md), [calidad](./03%20Calidad%20de%20c%C3%B3digo%20V_1_0_0.md), [seguridad](./04%20OWASP%20V_1_0_0.md) y [accesibilidad](./05%20WCAG%20V_1_0_0.md).

[← Volver al README Principal](../../../README.md)
