import base64
import io
from openai import OpenAI
from PIL import Image
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Imagen con IA", page_icon="🖼️", layout="wide"
)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown(
    """
    <style>
    .main { background-color: #0E1117; color: #F8FAFC; }
    .stSidebar { background-color: #161B22 !important; }
    .hero-title { color: #FFFFFF; font-weight: 800; font-size: 2.2rem; }
    .card-box {
        background-color: #161B22;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363D;
    }
    .stButton>button {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        color: white; font-weight: bold; border-radius: 8px; border: none;
        padding: 10px 20px; width: 100%;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- BARRA LATERAL: CONFIGURACIÓN ---
st.sidebar.markdown("### ⚙️ Configuración")
st.sidebar.markdown(
    "<p style='color: #9CA3AF; font-size: 13px;'>Inserta tu API Key para"
    " activar las funciones de análisis visual.</p>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

st.sidebar.markdown("**Clave API de OpenAI**")
openai_api_key = st.sidebar.text_input(
    "API Key",
    type="password",
    placeholder="sk-...",
    label_visibility="collapsed",
)

if not openai_api_key:
  st.sidebar.markdown(
      "<div"
      ' style="background-color: #3B3A2A; padding: 10px; border-radius: 6px;'
      ' color: #FACC15; font-size: 13px; font-weight: bold;">🔑 Ingresa tu API'
      " Key para comenzar</div>",
      unsafe_allow_html=True,
  )

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='color: #9CA3AF; font-size: 12px;'>Powered by gpt-4o 🚀</p>",
    unsafe_allow_html=True,
)

# --- CONTENIDO PRINCIPAL ---
st.markdown(
    '<p class="hero-title">Análisis de Imagen con IA 🤖🖼️</p>',
    unsafe_allow_html=True,
)
st.markdown(
    "Sube cualquier imagen para obtener un análisis descriptivo detallado o haz"
    " preguntas específicas sobre ella en tiempo real."
)
st.markdown("---")

# Estructura de dos columnas (1. Cargar Imagen / 2. Opciones de Análisis)
col1, col2 = st.columns(2)

uploaded_file = None

with col1:
  st.markdown("### 1. Cargar Imagen")
  uploaded_file = st.file_uploader(
      "Upload 200MB per file • JPG, PNG",
      type=["jpg", "jpeg", "png"],
      label_visibility="collapsed",
  )

with col2:
  st.markdown("### 2. Opciones de Análisis")
  custom_question_toggle = st.toggle("¿Quieres hacer una pregunta específica?")

  specific_question = ""
  if custom_question_toggle:
    specific_question = st.text_input(
        "Escribe tu pregunta sobre la imagen:",
        placeholder="Ej: ¿Qué objetos destacados aparecen en esta foto?",
    )

  analyze_btn = st.button("Analizar Imagen")

# --- PROCESAMIENTO Y VISUALIZACIÓN ---
if uploaded_file is not None:
  st.markdown("---")
  st.markdown("### 👁️ Vista Previa y Resultados")

  img_col1, img_col2 = st.columns(2)

  with img_col1:
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagen Cargada", use_container_width=True)

  with img_col2:
    if analyze_btn:
      if not openai_api_key:
        st.warning(
            "Por favor ingresa tu Clave API de OpenAI en la barra lateral para"
            " ejecutar el análisis visual."
        )
      else:
        with st.spinner("Analizando la imagen con GPT-4o..."):
          try:
            client = OpenAI(api_key=openai_api_key)

            # Convertir imagen a base64 para enviarla a la API de OpenAI
            buffered = io.BytesIO()
            image.save(buffered, format=image.format if image.format else "JPEG")
            img_bytes = buffered.getvalue()
            base64_image = base64.b64encode(img_bytes).decode("utf-8")

            # Definir el prompt según la selección del usuario
            if custom_question_toggle and specific_question.strip():
              prompt_text = (
                  f"Analiza la imagen proporcionada y responde detalladamente"
                  f" a la siguiente pregunta: {specific_question}"
              )
            else:
              prompt_text = (
                  "Proporciona un análisis descriptivo y detallado de esta"
                  " imagen, destacando sus elementos clave, colores, contexto"
                  " y cualquier detalle relevante."
              )

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": (
                                        f"data:image/jpeg;base64,{base64_image}"
                                    )
                                },
                            },
                        ],
                    }
                ],
                max_tokens=800,
            )

            analysis_result = response.choices[0].message.content
            st.markdown("#### 💡 Resultado del Análisis:")
            st.info(analysis_result)

          except Exception as e:
            st.error(
                f"Ocurrió un error al procesar la imagen con OpenAI: {e}"
            )
    else:
      st.info(
          "Configura tus opciones a la derecha y haz clic en **Analizar"
          " Imagen** para comenzar."
      )
