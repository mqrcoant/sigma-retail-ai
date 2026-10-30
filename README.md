# SIGMA Retail AI — Parcial 01
Prototipo académico con Data Mart SQLite, clases orientadas a objetos, persistencia ZODB e interfaz Streamlit. **Datos simulados**; resultados únicamente del Data Mart. El intérprete local es un catálogo determinista de intenciones y NO un LLM. La integración LLM opcional es una extensión prevista, no implementada.

## Entorno
Python 3.11+ recomendado. Instalar dependencias con `python -m pip install -r requirements.txt` (requiere Internet para la instalación inicial). Desde la raíz del proyecto:

```
python -m sigma.generate
python -m pytest -q
streamlit run app.py
```

ZODB conserva el historial en `data/sesiones.fs`. `data/sigmaretail.sqlite` es la base analítica; se regenera de forma reproducible con la semilla 42026. Cada arranque es local; no se requieren credenciales. No regenerar datos durante una demostración si se necesita preservar consistencia con el historial. No colocar `.fs`, claves o datos sensibles en repositorios públicos.

## Consultas
Diez familias en `sigma/catalog.py`; los SQL usan parámetros `:nombre`, no interpolación. `sigma/agent.py` interpreta preguntas en español con frases reconocibles, bloquea operaciones destructivas y devuelve evidencias. Consultas fuera del catálogo se rechazan de manera explícita. El lenguaje natural libre tiene cobertura limitada; no se debe anunciar como comprensión general.

## Arquitectura
`sql/01_schema.sql`: DDL; `sigma/generate.py`: ETL simulado; `sigma/catalog.py`: SQL controlado; `sigma/objects.py`: modelo OO; `sigma/store.py`: persistencia ZODB; `sigma/agent.py`: procesamiento; `app.py`: interfaz. `sql/02_controles.sql`: verificaciones. `tests/`: regresión automatizada.

## Datos y reglas
Grano: una línea de producto de un ticket. Importes en céntimos enteros: ingreso neto=bruto-descuento-devolución; margen bruto=ingreso neto-costo. Ticket promedio=SUM(neto)/COUNT(DISTINCT ticket_id). SCD2 del segmento: nueva fila con clave sustituta, vigencias disjuntas; historial se conserva. En este dataset la devolución es completa y el coste asociado es cero, como simplificación explícita. Un valor vacío no es cero. El volumen de compra se operacionaliza como unidades vendidas; la comparación de segmentos aplica el segmento histórico de cada operación.

## Limitaciones conocidas
Los datos son simulados, las reglas de clasificación de consultas son limitadas, el análisis tiene un solo año y no existe integración con ERP real. El SQL de comparativa de canales utiliza los últimos tres meses disponibles del calendario (2026-10 a 2026-12); en datos parciales debería determinarse por existencia de hechos. No hay servicio LLM integrado; el modo opcional queda como mejora futura. La persistencia ZODB exige instalar dependencias antes de demostrar la interfaz.