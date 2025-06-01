# Chatbot de la Diputación Foral de Bizkaia

Este proyecto es un chatbot interactivo construido con Gradio y Python. Utiliza un modelo de DeepSeek de Hugging Face para buscar trámites y se basa en 2 archivos para plasamar información sobre ayuntamientos y departamentos.

## Características

* Búsqueda de información de Ayuntamientos y Departamentos.
* Generación de respuestas sobre trámites usando el modelo DeepSeek-R1-0528 a través de Hugging Face Inference API.
* Interfaz de usuario simple y comoda con Gradio.

## Instalación y Uso

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/KimetzL/ChatbotDFB.git
    cd nombre-de-tu-repositorio
    ```
2.  **Obtén tu token de Hugging Face:**
    * Ve a [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) y crea un token de lectura (Read).
3.  **Ejecuta setup_chatbot.bat una vez instalado Python:**
    El chatbot se abrirá en tu navegador en `http://127.0.0.1:7860`.

## Uso del Chatbot

Puedes consultar información usando los siguientes formatos:

* **Ayuntamiento:** `Ayuntamiento: Bilbao`, `Municipio = Getxo`, `Pueblo : Galdakao`
* **Departamento:** `Departamento: Acción Social`, `Ministerio = Hacienda`, `Organismo = Turismo`
* **Trámite:** `Trámite: Modelo 561. Impuesto sobre la cerveza`, `Procedimiento = Reversión de expropiaciones`, `Servicio: Solicitud de certificado de Residencia Fiscal`

---
### Aviso Importante:
La información proporcionada por este chatbot puede no ser 100% fiable. Siempre contrástala con fuentes oficiales.

---
