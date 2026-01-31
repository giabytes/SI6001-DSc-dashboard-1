import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Explorador Universal con Slider", layout="wide")

st.title("📊 Explorador Universal de Datos Dinámico")
st.markdown("Carga cualquier CSV y usa la barra lateral para limitar el alcance del análisis.")

# --- BARRA LATERAL: CARGA Y CONTROL DE REGISTROS ---
st.sidebar.header("📂 1. Entrada de Datos")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo CSV", type=["csv"])

if uploaded_file is not None:
    try:
        # Carga inicial de datos
        df_raw = pd.read_csv(uploaded_file)
        total_filas = len(df_raw)

        # --- BARRA DE DESPLAZAMIENTO (SLIDER) ---
        st.sidebar.divider()
        st.sidebar.header("🔢 2. Control de Registros")
        
        # Slider para elegir cantidad de registros
        cantidad = st.sidebar.slider(
            "Selecciona la cantidad de registros a analizar:",
            min_value=1,
            max_value=total_filas,
            value=min(100, total_filas) # Valor por defecto: 100 o el total si es menor
        )
        
        # Aplicamos el recorte de datos basándonos en el slider
        df = df_raw.head(cantidad).copy()
        st.sidebar.info(f"Analizando los primeros {cantidad} registros de {total_filas} totales.")

        # --- DETECCIÓN AUTOMÁTICA DE TIPOS ---
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass

        cols_num = df.select_dtypes(include=[np.number]).columns.tolist()
        cols_cat = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
        cols_date = df.select_dtypes(include=['datetime64']).columns.tolist()

        # --- PESTAÑAS DE ANÁLISIS ---
        tab_cuant, tab_cual, tab_graf = st.tabs(["🔢 Cuantitativo", "📝 Cualitativo", "📊 Gráfico"])

        # 1. ANÁLISIS CUANTITATIVO
        with tab_cuant:
            st.subheader(f"Estadísticas de los {cantidad} registros")
            if cols_num:
                st.dataframe(df.describe().T, use_container_width=True)
                if len(cols_num) > 1:
                    st.markdown("**Matriz de Correlación**")
                    fig_corr = px.imshow(df[cols_num].corr(), text_auto=True, color_continuous_scale='Viridis')
                    st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.warning("No hay columnas numéricas para analizar.")

        # 2. ANÁLISIS CUALITATIVO
        with tab_cual:
            st.subheader("Distribución Categórica")
            if cols_cat:
                target_cat = st.selectbox("Analizar columna:", cols_cat)
                col_counts = df[target_cat].value_counts().reset_index()
                st.table(col_counts)
            else:
                st.warning("No hay columnas categóricas.")

        # 3. ANÁLISIS GRÁFICO
        with tab_graf:
            st.subheader("Visualización Dinámica")
            tipo_g = st.radio("Gráfico:", ["Barras", "Dispersión", "Líneas"], horizontal=True)
            
            c1, c2 = st.columns(2)
            with c1:
                gx = st.selectbox("Eje X:", cols_cat + cols_date + cols_num)
            with c2:
                gy = st.selectbox("Eje Y:", cols_num) if cols_num else st.selectbox("Eje Y:", cols_cat)
            
            if tipo_g == "Barras":
                fig = px.bar(df, x=gx, y=gy, color=cols_cat[0] if cols_cat else None)
            elif tipo_g == "Dispersión":
                fig = px.scatter(df, x=gx, y=gy, color=cols_cat[0] if cols_cat else None)
            else:
                fig = px.line(df, x=gx, y=gy)
                
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
        if st.button("Reintentar"):
            st.rerun()
else:
    st.info("Sube un archivo CSV para activar el slider y comenzar el análisis.")
