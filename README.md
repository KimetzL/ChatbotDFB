# Chatbot de la Diputación Foral de Bizkaia

Este proyecto es un chatbot interactivo construido con Gradio y Python. Utiliza modelos de Hugging Face para buscar información sobre Ayuntamientos, Departamentos y Trámites, basándose en datos locales.

## Características

* Búsqueda de información de Ayuntamientos y Departamentos.
* Generación de respuestas sobre trámites usando el modelo DeepSeek-R1-0528 a través de Hugging Face Inference API.
* Interfaz de usuario simple y comoda con Gradio.

## Instalación y Uso

1.  **Clona el repositorio:**
    ```intento
    clon)
    cd nombre-de-tu-repositorio
    ```
2.  **Crea un entorno virtual (recomendado):**
    ```intento
    python -m venv chatbot_env
    .\chatbot_env \ scripts \ activar # en windows
    # source chatbot_env/bin/activate # En macOS/Linux
    ```
3.  **Instala las dependencias:**
    ```intento
    PIP install -r requisitos.txt
    ```
4.  **Asegúrate de tener tus archivos CSV** en una carpeta `Datos/` en la misma raíz del proyecto:
    * `Data/Ayuntamientos.csv`
    * `Data/Departamentos.csv`
    * `Data/Tramites_resumidos.csv`
5.  **Obtén tu token de Hugging Face:**
    * Y un [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) y crea un token de lectura (Read).
    * **ATENCIÓN:** Por simplicidad, el token está actualmente hardcodeado en `chatbotGradioGPT3.py`. Para entornos de producción, se recomienda usar variables de entorno.
6.  **Ejecuta el chatbot:**
    ```intento
    Python chatbotgradiogpt3.py
    ```
    El chatbot se abrirá en tu navegador en `http://127.0.0.1:7860`.

## Uso del Chatbot

Puedes consultar información usando los siguientes formatos:

* **Ayuntamiento:** `Ayuntamiento: Bilbao`, `Municipio = Getxo`
* **Departamento:** `Departamento: Acción Social`, `Ministerio = Hacienda`
* **Trámite:** `Trámite: Modelo 561. Impuesto sobre la cerveza`, `Procedimiento = Reversión de expropiaciones`

---
### Aviso Importante:
La información proporcionada por este chatbot puede no ser 100% fiable. Siempre contrástala con fuentes oficiales.

---
