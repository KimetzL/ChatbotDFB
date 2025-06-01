@echo off
setlocal enabledelayedexpansion

:: Cambiar al directorio del script
cd /d %~dp0

:: Pedir token de Hugging Face
set /p HF_TOKEN=Introduce tu token de Hugging Face: 

echo.
echo Inyectando el token en ChatbotDFB.py...
powershell -Command "(Get-Content ChatbotDFB.py) -replace 'HF_API_TOKEN = \".*\"', 'HF_API_TOKEN = \"!HF_TOKEN!\"' | Set-Content ChatbotDFB.py"

echo.
echo Creando entorno virtual...
python -m venv chatbot_dfb

echo Activando entorno virtual...
call "%cd%\chatbot_dfb\Scripts\activate"

echo Instalando dependencias...
pip install --upgrade pip
pip install gradio pandas numpy torch transformers sentence-transformers faiss-cpu huggingface_hub rapidfuzz

echo.
echo Todo listo. Ejecutando el bot...
python ChatbotDFB.py

pause
