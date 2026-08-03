# Tarea de recompensa con dos opciones

Completarás un total de 40 juegos independientes. Cada juego consiste en una
serie de elecciones entre dos opciones: la opción A y la opción B.

Al comienzo de cada juego, realizarás cuatro elecciones forzadas. Durante estos
turnos de elección forzada, el estado actual de la tarea especificará qué opción
debes seleccionar. Después de completar las cuatro elecciones forzadas,
realizarás una o seis elecciones libres, en las que podrás elegir libremente
entre la opción A y la opción B.

Dentro de cada juego, los patrones de recompensa de las opciones A y B pueden
ser diferentes y no se te revelan de antemano. Después de cada elección,
recibirás información que muestra la recompensa de la opción seleccionada. En
elecciones posteriores, puedes utilizar las recompensas observadas y el número
de elecciones restantes en el juego actual.

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
