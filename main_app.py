import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Universal CSV Explorer", layout="wide")

st.title("📊 Explorador Universal de Datos")
st.markdown("Sube cualquier archivo CSV y analizaré sus dimensiones automáticamente.")

# --- CARGA DE DATOS ---
st.sidebar.header("📂 Entrada de Datos")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo CSV", type=["csv"])

if uploaded_file is not None:
    try:
        # Carga inicial
        df = pd.read_csv(uploaded_file)
        
        # --- DETECCIÓN AUTOMÁTICA DE TIPOS ---
        # Intentar convertir columnas que parecen fechas
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass

        # Separar tipos de columnas
        cols_num = df.select_dtypes(include=[np.number]).columns.tolist()
        cols_cat = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
        cols_date = df.select_dtypes(include=['datetime64']).columns.tolist()

        st.sidebar.success(f"Cargadas {df.shape[0]} filas y {df.shape[1]} columnas.")

        # --- FILTROS DINÁMICOS ---
        st.sidebar.divider()
        st.sidebar.subheader("🎯 Filtros Rápidos")
        if cols_cat:
            cat_to_filter = st.sidebar.selectbox("Filtrar por categoría:", ["Ninguno"] + cols_cat)
            if cat_to_filter != "Ninguno":
                val_filter = st.sidebar.multiselect(f"Valores de {cat_to_filter}", df[cat_to_filter].unique())
                if val_filter:
                    df = df[df[cat_to_filter].isin(val_filter)]

        # --- PESTAÑAS ---
        tab_cuant, tab_cual, tab_graf = st.tabs(["🔢 Cuantitativo", "📝 Cualitativo", "📊 Gráfico Dinámico"])

        # ==========================================
        # 1. ANÁLISIS CUANTITATIVO (NÚMEROS)
        # ==========================================
        with tab_cuant:
            if cols_num:
                st.subheader("Resumen Estadístico")
                st.dataframe(df.describe().T, use_container_width=True)
                
                st.divider()
                st.subheader("🔥 Correlación de Variables")
                if len(cols_num) > 1:
                    fig_corr = px.imshow(df[cols_num].corr(), text_auto=True, color_continuous_scale='RdBu_r')
                    st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.warning("No se detectaron columnas numéricas.")

        # ==========================================
        # 2. ANÁLISIS CUALITATIVO (CATEGORÍAS)
        # ==========================================
        with tab_cual:
            if cols_cat:
                c1, c2 = st.columns(2)
                with c1:
                    target_cat = st.selectbox("Contar valores de:", cols_cat)
                    st.write(df[target_cat].value_counts())
                with c2:
                    if len(cols_cat) > 1:
                        st.subheader("Cruce de Categorías")
                        c_row = st.selectbox("Filas:", cols_cat, index=0)
                        c_col = st.selectbox("Columnas:", cols_cat, index=1)
                        st.dataframe(pd.crosstab(df[c_row], df[c_col]), use_container_width=True)
            else:
                st.warning("No se detectaron columnas categóricas.")

        # ==========================================
        # 3. ANÁLISIS GRÁFICO (EXPLORACIÓN)
        # ==========================================
        with tab_graf:
            tipo_g = st.selectbox("Tipo de Gráfico:", ["Barras", "Dispersión", "Histograma", "Líneas"])
            
            gc1, gc2, gc3 = st.columns(3)
            
            with gc1:
                # Eje X: Puede ser categórico o fecha
                x_options = cols_cat + cols_date + cols_num
                gx = st.selectbox("Eje X:", x_options)
            with gc2:
                # Eje Y: Normalmente numérico
                gy = st.selectbox("Eje Y:", cols_num if cols_num else x_options)
            with gc3:
                gcol = st.selectbox("Color por:", ["Ninguno"] + cols_cat)
            
            color_param = gcol if gcol != "Ninguno" else None

            if tipo_g == "Barras":
                fig = px.bar(df, x=gx, y=gy, color=color_param, barmode="group")
            elif tipo_g == "Dispersión":
                fig = px.scatter(df, x=gx, y=gy, color=color_param)
            elif tipo_g == "Histograma":
                fig = px.histogram(df, x=gx, color=color_param)
            elif tipo_g == "Líneas":
                fig = px.line(df, x=gx, y=gy, color=color_param)

            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error al procesar el dataset: {e}")
        st.button("Intentar de nuevo")

else:
    st.info("Esperando archivo CSV... Sube uno en el panel de la izquierda.")
