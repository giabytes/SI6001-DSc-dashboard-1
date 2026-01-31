import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from groq import Groq # ¡No olvides añadir 'groq' a tu requirements.txt!

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="💖 AI Data Bestie 🎀", page_icon="🌸", layout="wide")

# --- ESTILOS CSS GIRLY (Resumido para espacio) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF0F5; }
    h1 { color: #FF69B4; text-align: center; font-family: 'Georgia'; }
    .stMetric { background-color: #FFFFFF; border-radius: 12px; border-left: 5px solid #FFD1DC; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { background-color: #FFD1DC; border-radius: 10px; color: #FF69B4; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("💖 AI Data Bestie: Insights con Estilo 🎀")

# --- BARRA LATERAL ---
st.sidebar.header("🌸 Configuración Chic")
groq_api_key = st.sidebar.text_input("Introduce tu Groq API Key:", type="password", placeholder="gsk_...")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo CSV aquí:", type=["csv"])

if uploaded_file is not None:
    df_raw = pd.read_csv(uploaded_file)
    
    st.sidebar.divider()
    cantidad = st.sidebar.slider("¿Cuántos registros analizamos, linda?", 1, len(df_raw), min(200, len(df_raw)))
    df = df_raw.head(cantidad).copy()

    # Detección de tipos
    for col in df.columns:
        if df[col].dtype == 'object':
            try: df[col] = pd.to_datetime(df[col], errors='coerce')
            except: pass

    cols_num = df.select_dtypes(include=[np.number]).columns.tolist()
    cols_cat = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()

    # --- PESTAÑAS ---
    tab_cuant, tab_cual, tab_graf, tab_ai = st.tabs([
        "🔢 Cuantitativo", "📝 Cualitativo", "📊 Gráficos", "🤖 AI Bestie Insights"
    ])

    # (Las pestañas anteriores se mantienen igual, aquí nos enfocamos en la de AI)
    with tab_cuant:
        st.subheader("🌸 Resumen Glamuroso")
        st.dataframe(df.describe().T, use_container_width=True)

    with tab_cual:
        st.subheader("🎀 Categorías con Style")
        if cols_cat:
            st.write(df[cols_cat[0]].value_counts())

    with tab_graf:
        st.subheader("🌈 Visualización")
        if cols_num:
            fig = px.histogram(df, x=cols_num[0], color_discrete_sequence=['#FFB6C1'])
            st.plotly_chart(fig, use_container_width=True)

    # ==========================================
    # PESTAÑA NUEVA: AI ASSISTANT (GROQ)
    # ==========================================
    with tab_ai:
        st.header("🤖 ¡Habla con tu AI Data Bestie!")
        
        if not groq_api_key:
            st.warning("🔑 Necesitas poner tu API Key de Groq en la barra lateral para que la magia funcione.")
        else:
            st.markdown("### ✨ Análisis de Hallazgos")
            
            # Preparamos un contexto pequeño para el LLM
            stats_summary = df.describe(include='all').to_string()
            
            prompt = f"""
            Actúa como una experta analista de datos que es súper 'girly', moderna y divertida. 
            Usa emojis y vocabulario tipo 'bestie', 'slay', 'chic', 'aesthetic'.
            Analiza el siguiente resumen de datos y describe 3 hallazgos o tendencias importantes que encuentres. 
            Sé clara pero con mucho estilo.

            Datos para analizar:
            {stats_summary}
            """

            if st.button("✨ ¡Generar Insights Divinos!"):
                try:
                    client = Groq(api_key=groq_api_key)
                    with st.spinner("🎀 Consultando con mi bola de cristal... digo, con Llama 3.3"):
                        completion = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.7,
                            max_tokens=1024,
                        )
                        
                        response = completion.choices[0].message.content
                        
                        st.markdown("---")
                        st.markdown(response)
                        st.balloons()
                except Exception as e:
                    st.error(f"💔 ¡Ups! Algo salió mal con la conexión: {e}")

else:
    st.info("🌟 Sube tu archivo para empezar el análisis con IA, ¡te va a encantar!")

st.divider()
st.caption("💕 Powered by Groq & Llama 3.3 • Stay Aesthetic ✨")
