# ========= IMPORTACIÓN LIBRERIAS =========

import gradio as gr
import pandas as pd
import numpy as np
import faiss
import re
from sentence_transformers import SentenceTransformer, util
from huggingface_hub import InferenceClient
from rapidfuzz import process, fuzz


# ========= 1. CONFIGURACIÓN HF =========
HF_API_TOKEN = "HF_API_TOKEN"  # ¡Reemplaza esto con tu token real de HuggingFace!
MODEL_NAME = "deepseek-ai/DeepSeek-R1-0528"
client = InferenceClient(token=HF_API_TOKEN, model=MODEL_NAME)
embedding_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# ========= 2. CARGA Y PREPROCESAMIENTO DE DATOS =========
def cargar_embeddings(csv_path, columna, sep=","):
    df = pd.read_csv(csv_path, delimiter=sep)
    df.reset_index(drop=True, inplace=True)
    df["embedding"] = df[columna].apply(lambda x: embedding_model.encode(str(x).lower(), convert_to_numpy=True))
    return df

df_ayu = cargar_embeddings("Data/Ayuntamientos.csv", "Ayuntamiento")
df_dep = cargar_embeddings("Data/Departamentos.csv", "Departamento", sep=";")

df_tra = pd.read_csv("Data/Tramites_resumidos.csv", delimiter=";", encoding="utf-8-sig")
df_tra.reset_index(drop=True, inplace=True)

textos_tramites = []
metadatos_tramites = []

# Esto ayuda a evitar pasarse de tokens y optimizar el csv de Tramites
for _, row in df_tra.iterrows():
    descripcion = str(row.get("DENOMINACION", ""))
    
    if len(descripcion) > 3000:
        descripcion = descripcion[:3000] + "..."
    
    texto = f"Trámite: {row.get('DENOMINACION', '')}\nDepartamento: {row.get('DEPARTAMENTO', '')}\nDescripción: {descripcion}"
    textos_tramites.append(texto)
    metadatos_tramites.append({
        "tramite": row.get("DENOMINACION", ""),
        "departamento": row.get("DEPARTAMENTO", "")
    })

tramite_embeddings = np.array(embedding_model.encode(textos_tramites, convert_to_numpy=True)).astype("float32")
index_tramites = faiss.IndexFlatL2(tramite_embeddings.shape[1])
index_tramites.add(tramite_embeddings)

# ========= 3. FUNCIONES DE BÚSQUEDA =========
def buscar_similitud(pregunta, df, col):
    pregunta_embedding = embedding_model.encode(pregunta.lower(), convert_to_numpy=True)
    lista_embeddings = np.vstack(df["embedding"].values).astype("float32")
    if lista_embeddings.shape[0] == 0:
        raise ValueError("❌ No hay embeddings cargados para comparar.")
    cos_sim = util.cos_sim(pregunta_embedding, lista_embeddings)[0]
    idx = int(np.argmax(cos_sim))
    return df.iloc[idx], float(cos_sim[idx])

def buscar_tramite(pregunta):
    pregunta_embedding = np.array(embedding_model.encode([pregunta.lower()], convert_to_numpy=True)).astype("float32")
    _, indices = index_tramites.search(pregunta_embedding, k=1)
    idx = indices[0][0]
    return textos_tramites[idx], metadatos_tramites[idx]

def generar_respuesta(contexto, pregunta):
    messages = [
        {"role": "system", "content": "Eres un asistente útil que proporciona información sobre trámites gubernamentales, ayuntamientos y departamentos. Responde de manera concisa basándote solo en la información proporcionada."},
        {"role": "user", "content": f"Toda la información:\n{contexto}\n\nQuiero información sobre: {pregunta}\nResponde solo si coincide con la algo de la parte de Toda la información:"}
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=150,    # 'max_tokens' para chat completion
            temperature=0.8,
            top_p=0.95,
        )

        if response.choices and response.choices[0].message and response.choices[0].message.content:
            texto_generado = response.choices[0].message.content
        else:
            texto_generado = "No se pudo obtener una respuesta válida del modelo (respuesta de chat completion vacía)."

        return texto_generado.split("Respuesta:")[-1].strip() if "Respuesta:" in texto_generado else texto_generado.strip()

    except Exception as e:
        print(f"Error al llamar a la API de Hugging Face: {e}")
        return "Disculpa, hubo un problema al generar la respuesta. El modelo no está respondiendo como se espera. Por favor, verifica el token o intenta de nuevo más tarde."


# ========= 4. UTILIDADES =========
# Diccionario de palabras clave fuzzy por categoría
KEYWORDS = {
    "ayuntamiento": ["ayuntamiento", "ciudad", "pueblo", "municipio"],
    "departamento": ["departamento", "administración", "ministerio", "organismo"],
    "trámite": ["trámite", "tramite", "procedimiento", "servicio"]
}

def fuzzy_match_key(line, threshold=80):

    import re
    match = re.match(r"^\s*([^:=]+)\s*[:=]\s*(.+)$", line)
    if not match:
        return None, None

    clave_raw = match.group(1).strip().lower()
    valor = match.group(2).strip()

    for categoria, palabras in KEYWORDS.items():
        mejor, ratio, _ = process.extractOne(clave_raw, palabras, scorer=fuzz.ratio)
        if ratio >= threshold:
            return categoria, valor

    return None, None


# ========= 5. FUNCIÓN PRINCIPAL =========

def responder(pregunta):
    pregunta = pregunta.strip()
    categoria, valor = fuzzy_match_key(pregunta)

    if categoria is None or not valor:
        return "🤖 No entendí tu consulta. Usa un formato como 'Trámite: renovar DNI' o 'Ayuntamiento: Bilbao'"

    if categoria == "trámite":
        texto_tramite, _ = buscar_tramite(valor)
        return generar_respuesta(texto_tramite, valor)

    if categoria == "ayuntamiento":
        mejor_ayto, sim = buscar_similitud(valor, df_ayu, "Ayuntamiento")
        if sim > 0.6:
            return (
                f"<span style='font-size:1.5em;'>🏛️</span> "
                f"<span style='font-size:20px; font-weight:bold;'>AYUNTAMIENTO:</span> "
                f"<span style='font-size:17px;'>{mejor_ayto['Ayuntamiento']}</span><br>"
                f"<span style='font-size:1.5em;'>📍</span> "
                f"<span style='font-size:20px; font-weight:bold;'>DIRECCIÓN:</span> "
                f"<span style='font-size:17px;'>{mejor_ayto['Dirección']}</span><br>"
                f"<span style='font-size:1.5em;'>📞</span> "
                f"<span style='font-size:20px; font-weight:bold;'>TELÉFONO:</span> "
                f"<span style='font-size:17px;'>{mejor_ayto['Teléfono']}</span><br>"
                f"<span style='font-size:1.5em;'>📧</span> "
                f"<span style='font-size:20px; font-weight:bold;'>EMAIL:</span> "
                f"<span style='font-size:17px;'>{mejor_ayto.get('Email', 'No disponible')}</span><br>"
                f"<span style='font-size:1.5em;'>🔗</span> "
                f"<span style='font-size:20px; font-weight:bold;'>UBICACIÓN EN MAPS:</span> "
                f"<a href='{mejor_ayto.get('Enlace maps', '#')}' target='_blank' style='font-size:17px;'>{mejor_ayto.get('Enlace maps', 'No disponible')}</a><br>"
                f"<span style='font-size:1.5em;'>🕒</span> "
                f"<span style='font-size:20px; font-weight:bold;'>HORARIO:</span> "
                f"<span style='font-size:17px;'>{mejor_ayto['Horario']}</span><br>"
                f"<span style='font-size:1.5em;'>🌐</span> "
                f"<span style='font-size:20px; font-weight:bold;'>WEB OFICIAL:</span> "
                f"<a href='{mejor_ayto.get('Web', '#')}' target='_blank' style='font-size:17px;'>{mejor_ayto.get('Web', 'No disponible')}</a>"
            )
        return "🤖 No encontré ningún ayuntamiento que coincida con tu consulta."

    if categoria == "departamento":
        mejor_dep, sim = buscar_similitud(valor, df_dep, "Departamento")
        if sim > 0.6:
            return (
                f"<span style='font-size:1.5em;'>🏢</span> "
                f"<span style='font-size:20px; font-weight:bold;'>DEPARTAMENTO:</span> "
                f"<span style='font-size:17px;'>{mejor_dep['Departamento']}</span><br>"
                f"<span style='font-size:1.5em;'>📍</span> "
                f"<span style='font-size:20px; font-weight:bold;'>DIRECCIÓN:</span> "
                f"<span style='font-size:17px;'>{mejor_dep['Dirección']}</span><br>"
                f"<span style='font-size:1.5em;'>📞</span> "
                f"<span style='font-size:20px; font-weight:bold;'>TELÉFONO:</span> "
                f"<span style='font-size:17px;'>{mejor_dep['Teléfono']}</span><br>"
                f"<span style='font-size:1.5em;'>🔗</span> "
                f"<span style='font-size:20px; font-weight:bold;'>UBICACIÓN EN MAPS:</span> "
                f"<a href='{mejor_dep.get('Enlace maps', '#')}' target='_blank' style='font-size:17px;'>{mejor_dep.get('Enlace maps', 'No disponible')}</a><br>"
                f"<span style='font-size:1.5em;'>🕒</span> "
                f"<span style='font-size:20px; font-weight:bold;'>HORARIO:</span> "
                f"<span style='font-size:17px;'>{mejor_dep['Horario']}</span>"
            )
        return "🤖 No encontré ningún departamento que coincida con tu consulta."

# ========== 6. Interfaz Gradio ==========

# Definimos el tema
theme = gr.themes.Soft(
    primary_hue="blue",
    font=[gr.themes.GoogleFont("Inter"), "sans-serif"]
)

iface = gr.Interface(
    fn=responder,
    inputs=gr.Textbox(
        lines=2,
        label="Tu consulta❓",
        placeholder="Ej. Ayuntamiento: Bilbao | Procedimiento = Reversión de expropiaciones",
    ),
    outputs=gr.HTML(label="📌 Respuesta"),
    title="🤖 Chatbot de la Diputación Foral de Bizkaia",

description=(
    "<div style='padding: 0.5em; background-color: #fff3cd; color: black; border: 1px solid #ffeeba; border-radius: 8px; font-size: 17px;'>"
    "⚠️ <b style='color: black !important;'>Aviso:</b> La información puede no ser fiable. Contrástala siempre con fuentes oficiales."
    "</div><br>"

    "<div style='font-size: 17px; font-weight: bold; margin-top: 16px;'>🏛️ ¿Quieres consultar un ayuntamiento? Usa uno de estos prefijos, seguido de dos puntos (<code>:</code>) o del signo igual (<code>=</code>):</div>"
    "<ul style='margin-top: 8px;'>"
    "<li><b>Ayuntamiento, ciudad, pueblo o municipio</b></li>"
    "<li>Ejemplos: <code>Ayuntamiento: Bilbao</code>, <code>Municipio = Getxo</code>, <code>Pueblo : Galdakao</code></li>"
    "</ul>"

    "<div style='font-size: 17px; font-weight: bold; margin-top: 16px;'>🏢 ¿Y un departamento? También puedes indicarlo con <code>:</code> o <code>=</code>:</div>"
    "<ul style='margin-top: 8px;'>"
    "<li><b>Departamento, administración, ministerio u organismo</b></li>"
    "<li>Ejemplos: <code>Departamento: Acción Social</code>, <code>Ministerio = Hacienda</code>, <code>Organismo = Turismo</code></li>"
    "</ul>"

    "<div style='font-size: 17px; font-weight: bold; margin-top: 16px;'>📌 ¿Quieres consultar un trámite? Usa uno de estos formatos, seguido de <code>:</code> o <code>=</code>:</div>"
    "<ul style='margin-top: 8px;'>"
    "<li><b>Trámite, procedimiento o servicio</b></li>"
    "<li>Ejemplos: <code>Trámite: Modelo 561. Impuesto sobre la cerveza</code>, <code>Procedimiento = Reversión de expropiaciones</code>, <code>Servicio: Solicitud de certificado de Residencia Fiscal</code></li>"
    "</ul>"

    "<div style='font-size: 16px; margin-top: 16px;'>🔍 Para otras consultas, escribe tu duda de forma natural.</div>"
),
    theme=theme,
    live=False,
    submit_btn="🔎 Consultar",
    flagging_mode="never",
)

if __name__ == "__main__":
    iface.launch(inbrowser=True)
