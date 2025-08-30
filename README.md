# Agentes Compras Públicas

Este proyecto permite analizar datos de compras públicas de **Ecuador**, **Chile** y **Colombia** usando agentes inteligentes y generar un informe comparativo profesional.

## ¿Cómo usar?

En el archivo `main.py` puedes:

- **Elegir el año** que deseas analizar.
- **Seleccionar el tipo de compras públicas** (por ejemplo, subasta inversa).
- **Escoger los países** entre Ecuador, Chile y Colombia para el análisis.

Solo ajusta el prompt o los parámetros en el `main` según tus necesidades.

## ¿Qué genera el sistema?

Al finalizar el flujo, se crea automáticamente un **informe PDF** en la carpeta [`dist/`](dist/) con:

- Una **tabla** con los presupuestos totales en dólares para las categorías:
  - Salud
  - Educación
  - Infraestructura
- Un **gráfico de barras** comparativo entre los países.

## Ejemplo de uso

```python
# main.py
prompt = (
    "Analiza los datos de compras públicas del 2023 de procesos de subasta inversa "
    "de Ecuador, Chile y Colombia, y genera el informe final."
)
response = Runner.run_sync(orchestrator_agent, input=prompt)
print(response)
```

## Carpeta de informes

El informe final se guarda en la carpeta:

```
dist/informe_presupuesto.pdf
```

---

¡Explora, analiza y compara el gasto público de los países de manera fácil y visual!