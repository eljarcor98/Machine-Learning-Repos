import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import sys

# Ajustar ruta para importar desde src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db import get_session, NewsArticle, init_db

# Asegurar que la base de datos esté inicializada
init_db()

st.set_page_config(page_title="Análisis NLP OSINT", layout="wide", page_icon="📊")

# Global CSS for consistency and hiding sidebar
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');
    
    /* Use a more targeted font application to avoid overlapping/layout issues */
    html, body, st.markdown, .stApp { 
        font-family: 'Montserrat', sans-serif !important; 
    }
    
    /* Force line-height in all streamlit elements to prevent "montadas" (overlapping) text */
    div[data-testid="stMarkdownContainer"] p, 
    div[data-testid="stAlertContentInfo"] p, 
    div[data-testid="stCaptionContainer"] p {
        line-height: 1.6 !important;
        margin-bottom: 0.5rem !important;
    }

    .stApp { animation: vanishIn 0.6s ease-out; }
    @keyframes vanishIn { 0% { opacity: 0; transform: scale(0.98); } 100% { opacity: 1; transform: scale(1); } }
    [data-testid="stSidebar"], [data-testid="stSidebarCollapseButton"], div[data-testid="stSidebarNav"] { display: none !important; }
    .return-btn {
        display: inline-block;
        padding: 8px 16px;
        background-color: #3b82f6;
        color: white !important;
        text-decoration: none;
        border-radius: 8px;
        font-weight: 600;
        font-family: 'Montserrat', sans-serif;
        transition: background-color 0.3s ease;
        border: none;
        cursor: pointer;
    }
    .return-btn:hover { background-color: #2563eb; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# Return button
st.markdown('<a href="/" target="_self" class="return-btn">⬅️ Volver al Index</a>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.title("📊 Análisis de Narrativas (NLP)")
st.markdown("Análisis de frecuencia de palabras y tópicos extraídos de la base de inteligencia.")

with st.expander("🛠️ Metodología y Modelado de Datos", expanded=True):
    st.markdown("""
    ### 🧬 Pipeline de Inteligencia NLP
    El sistema procesa grandes volúmenes de texto no estructurado para extraer patrones significativos. El flujo de trabajo se divide en cuatro etapas principales:

    **1. Ingesta de Datos (Data Ingestion):**
    - **Fuentes:** Se implementaron conectores automatizados para extraer información de **GNews**, **RSS feeds** especializados y el dataset **GDELT**.
    - **Persistencia:** Los datos se almacenan en una base de datos relacional (SQLite) mediante un ORM (SQLAlchemy), permitiendo el almacenamiento histórico de títulos y descripciones.

    **2. Preprocesamiento (Preprocessing):**
    - **Limpieza:** Se realiza una normalización de texto (conversión a minúsculas).
    - **Tokenización:** El corpus se divide en palabras individuales utilizando expresiones regulares para eliminar ruido y caracteres especiales.
    - **Filtrado:** Se aplica un filtro de *Stop Words* (palabras comunes sin valor semántico como "de", "la", "the", "and") y se eliminan términos con longitud inferior a 4 caracteres para mejorar la precisión del análisis.

    **3. Modelado y Análisis (Modeling):**
    - **Análisis de Frecuencia:** Se utiliza la clase `Counter` para cuantificar la recurrencia de términos, identificando los temas dominantes en el discurso actual.
    - **Visualización Semántica:** Se genera una **Nube de Palabras (WordCloud)** donde el tamaño de cada término es proporcional a su frecuencia, permitiendo una detección rápida de tópicos críticos.
    - **Soporte de Datos:** El sistema está diseñado para ser escalable, permitiendo la futura integración de modelos de **LDA (Latent Dirichlet Allocation)** para detección de tópicos latentes y análisis de sentimientos.

    **4. Visualización (Dashboarding):**
    - Implementación de una interfaz interactiva con **Streamlit**, **Plotly** y **Matplotlib** para transformar datos crudos en inteligencia accionable.
    """)

st.markdown("---")
with st.expander("📝 Resumen de Trabajo Realizado", expanded=True):
    st.markdown("""
    ### 🚀 Logros y Ejecución del Proyecto
    Se ha desarrollado un módulo completo de procesamiento de lenguaje natural orientado a la inteligencia de fuentes abiertas (OSINT). Los hitos alcanzados incluyen:

    - **Infraestructura de Datos:** Creación de una base de datos relacional optimizada para el almacenamiento de artículos de noticias, permitiendo consultas rápidas y persistencia de datos.
    - **Automatización de Captura:** Desarrollo de scripts de extracción automática mediante la integración de APIs de noticias y feeds RSS, asegurando un flujo constante de información actualizada.
    - **Refinamiento de Texto:** Implementación de una arquitectura de limpieza de datos que elimina ruido semántico (stop-words) y normaliza el texto, incrementando la precisión de los términos extraídos.
    - **Análisis Estadístico:** Programación de un motor de conteo de frecuencias basado en `collections.Counter` para identificar tendencias globales en tiempo real.
    - **Inteligencia Visual:** Integración de herramientas de visualización avanzada como *WordClouds* y gráficos de barras interactivos para facilitar la interpretación rápida de narrativas complejas.
    - **Despliegue de Dashboard:** Consolidación de todas las etapas en una interfaz de usuario profesional y responsiva utilizando Streamlit.
    """)

# --- Carga de Datos ---
@st.cache_data(ttl=600)
def load_nlp_data():
    session = get_session()
    try:
        # Obtenemos el texto de todos los artículos
        articles = session.query(NewsArticle.title, NewsArticle.description).all()
        if not articles:
            return ""
        
        texts = []
        for title, desc in articles:
            # Asegurar que title no sea None
            t = title if title else ""
            d = desc if desc else ""
            texts.append(f"{t} {d}")
            
        return " ".join(texts)
    except Exception as e:
        st.error(f"Error al cargar datos para NLP: {e}")
        return ""
    finally:
        session.close()

corpus = load_nlp_data()

if corpus:
    # --- Nube de Palabras ---
    st.subheader("☁️ Nube de Palabras Clave")
    st.info("Visualización de los términos más recurrentes en las noticias monitoreadas.")
    
    wc = WordCloud(
        width=1200, 
        height=600, 
        background_color="white",
        colormap="viridis",
        max_words=100,
        contour_width=3,
        contour_color='steelblue'
    ).generate(corpus)

    fig, ax = plt.subplots(figsize=(20, 10))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)

    # --- Análisis de Frecuencia ---
    st.markdown("---")
    st.subheader("📈 Top de Términos")
    
    # Conteo simple de palabras (sin stop-words complejas para mantener velocidad)
    from collections import Counter
    import re

    words = re.findall(r'\w+', corpus.lower())
    # Lista básica de stop words en español e inglés
    stop_words = {'de', 'la', 'que', 'el', 'en', 'lo', 'del', 'se', 'los', 'un', 'una', 'con', 'por', 'para', 'las', 'the', 'and', 'a', 'of', 'to', 'in', 'is', 'it', 'that', 'as', 'for', 'was', 'with', 'on'}
    filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
    
    word_counts = Counter(filtered_words).most_common(20)
    df_words = pd.DataFrame(word_counts, columns=['Palabra', 'Frecuencia'])

    fig_bar = px.bar(
        df_words, 
        x='Palabra', 
        y='Frecuencia', 
        color='Frecuencia',
        color_continuous_scale='Viridis',
        title="Términos más frecuentes en el corpus"
    )
    st.plotly_chart(fig_bar, width='stretch')

    st.caption("Nota: Este análisis se basa en la frecuencia bruta de términos. Para un análisis de tópicos más avanzado, se sugiere el uso de LDA (Latent Dirichlet Allocation).")
else:
    st.warning("No hay datos suficientes en la base de datos para generar el análisis NLP.")