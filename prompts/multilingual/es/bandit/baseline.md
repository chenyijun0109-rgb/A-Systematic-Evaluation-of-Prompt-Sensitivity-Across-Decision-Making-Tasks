# Tarea de recompensa con dos opciones

Completarás 40 juegos independientes. En cada juego, realizarás una serie de
elecciones entre la opción A y la opción B.

Cada juego comienza con cuatro elecciones forzadas. En un turno de elección
forzada, el estado actual de la tarea te indica qué opción debes elegir. Después
de estas cuatro elecciones, realizarás una o seis elecciones libres entre A y B.

Dentro de un juego, A y B pueden tener diferentes patrones de recompensa que no
conoces de antemano. Después de cada elección, se te muestra la recompensa de la
opción seleccionada. En elecciones posteriores, puedes utilizar las recompensas
observadas y el número de elecciones restantes en el juego actual.

Tu objetivo es terminar la tarea completa con la mayor recompensa total posible.

Estado actual de la tarea:

```text
{observation}
```

Respuestas válidas:

```text
CHOICE: A
CHOICE: B
```

Responde exactamente con una respuesta válida y sin texto adicional.
