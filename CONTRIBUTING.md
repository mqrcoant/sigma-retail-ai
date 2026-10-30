# Desarrollo y pruebas

1. Crear un entorno virtual con Python 3.11 o posterior.
2. Instalar dependencias: `python -m pip install -r requirements.txt`.
3. Generar la base de ejemplo: `python -m sigma.generate`.
4. Ejecutar las pruebas: `python -m pytest -q`.
5. Iniciar la interfaz: `streamlit run app.py`.

Todos los datos del proyecto son sintéticos. Las métricas comerciales proceden exclusivamente del Data Mart. No publicar archivos de persistencia de sesiones ni credenciales. La integración con un LLM es una mejora futura; no se debe presentar como implementada.
