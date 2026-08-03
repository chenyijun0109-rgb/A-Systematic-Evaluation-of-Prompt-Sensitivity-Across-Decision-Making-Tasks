# Tarea de ganancias con globos

Completarás un total de 40 globos. Para cada globo, elegirás entre dos acciones:
inflar el globo o cobrar las ganancias.

Cada vez que inflas el globo con éxito, se añaden 0.05 a las ganancias temporales
de ese globo. Después de cada inflado exitoso, decidirás de nuevo si continúas
inflando o si cobras. Inflar también puede hacer que el globo explote. Si el
globo explota, se pierden todas las ganancias temporales de ese globo y la tarea
continúa con el siguiente globo.

Si eliges cobrar, las ganancias temporales acumuladas del globo actual se añaden
a tus ganancias totales y la tarea continúa con el siguiente globo.

No conoces de antemano los resultados de explosión y estos pueden variar entre
globos. En globos posteriores, puedes utilizar la información y los resultados
de globos anteriores.

Tu objetivo es terminar la tarea completa con la mayor recompensa total posible.

Estado actual de la tarea:

```text
{observation}
```

Respuestas válidas:

```text
ACTION: PUMP
ACTION: CASH_OUT
```

Responde exactamente con una respuesta válida y sin texto adicional.
