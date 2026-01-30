import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard Energético 360°",
    page_icon="⚡",
    layout="wide"
)

# --- ESTILOS CSS PERSONALIZADOS (Opcional para mejorar estética) ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    div.stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- TÍTULO ---
st.title("⚡ Dashboard de Análisis: Energías Renovables")
st.markdown("Un enfoque tridimensional: **Cuantitativo, Cualitativo y Gráfico**.")

# --- BARRA LATERAL: CARGA Y FILTROS GLOBALES ---
st.sidebar.header("1. Carga de Datos")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo CSV", type=["csv"])

# Lógica de carga
df = None
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        
        # Validación de columnas mínimas
        cols_req = ['Tecnologia', 'Operador', 'Capacidad_Instalada_MW']
        if not all(col in df.columns for col in cols_req):
            st.error("El archivo no contiene las columnas requeridas.")
            st.stop()

        # Preprocesamiento
        if 'Fecha_Entrada_Operacion' in df.columns:
            df['Fecha_Entrada_Operacion'] = pd.to_datetime(df['Fecha_Entrada_Operacion'])
            df['Año'] = df['Fecha_Entrada_Operacion'].dt.year

        st.sidebar.success("Datos cargados correctamente")
        
        # --- FILTROS GLOBALES (Afectan a las 3 pestañas) ---
        st.sidebar.divider()
        st.sidebar.header("2. Filtros Globales")
        
        # Filtros dinámicos basados en el dataset
        tech_options = df['Tecnologia'].unique()
        sel_tech = st.sidebar.multiselect("Tecnología", tech_options, default=tech_options)
        
        op_options = df['Operador'].unique()
        sel_op = st.sidebar.multiselect("Operador", op_options, default=op_options)
        
        # Aplicar filtros
        df_filtered = df[
            (df['Tecnologia'].isin(sel_tech)) & 
            (df['Operador'].isin(sel_op))
        ]
        
        if df_filtered.empty:
            st.warning("No hay datos con los filtros actuales.")
            st.stop()
            
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        st.stop()
else:
    st.info("👋 Por favor, carga el archivo 'energia_renovable.csv' en la barra lateral para comenzar.")
    st.stop()

# --- INTERFAZ PRINCIPAL DIVIDIDA EN 3 PARTES ---
st.divider()

# Definimos las pestañas
tab_cuant, tab_cual, tab_graf = st.tabs([
    "🔢 1. Análisis Cuantitativo", 
    "📝 2. Análisis Cualitativo", 
    "📊 3. Análisis Gráfico"
])

# ==========================================
# PARTE 1: ANÁLISIS CUANTITATIVO
# ==========================================
with tab_cuant:
    st.header("Análisis Numérico y Estadístico")
    st.markdown("Resumen de las variables numéricas clave del dataset.")

    # 1.1 KPIs
    cols_num = df_filtered.select_dtypes(include=[np.number]).columns
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Registros", df_filtered.shape[0])
    
    if 'Capacidad_Instalada_MW' in df_filtered.columns:
        c2.metric("Capacidad Total (MW)", f"{df_filtered['Capacidad_Instalada_MW'].sum():,.2f}")
        c3.metric("Capacidad Promedio", f"{df_filtered['Capacidad_Instalada_MW'].mean():,.2f}")
    
    if 'Inversion_Inicial_MUSD' in df_filtered.columns:
        c4.metric("Inversión Total (MUSD)", f"${df_filtered['Inversion_Inicial_MUSD'].sum():,.2f}")

    st.divider()

    # 1.2 Estadísticas Descriptivas
    col_desc1, col_desc2 = st.columns([1, 2])
    
    with col_desc1:
        st.subheader("Selecciona Variable")
        var_stats = st.selectbox("Variable para analizar en detalle:", cols_num)
        
        # Mostrar stats específicos de esa variable
        series = df_filtered[var_stats]
        st.write(f"**Mínimo:** {series.min()}")
        st.write(f"**Máximo:** {series.max()}")
        st.write(f"**Mediana:** {series.median()}")
        st.write(f"**Desviación Std:** {series.std():.2f}")

    with col_desc2:
        st.subheader("Tabla Descriptiva Completa")
        st.dataframe(df_filtered.describe().T, use_container_width=True)

    # 1.3 Matriz de Correlación
    st.subheader("🔥 Matriz de Correlación")
    st.markdown("¿Qué variables numéricas están relacionadas entre sí?")
    
    if len(cols_num) > 1:
        corr_matrix = df_filtered[cols_num].corr()
        fig_corr = px.imshow(corr_matrix, text_auto=True, aspect="auto", color_continuous_scale="RdBu_r")
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.warning("No hay suficientes columnas numéricas para correlación.")

# ==========================================
# PARTE 2: ANÁLISIS CUALITATIVO
# ==========================================
with tab_cual:
    st.header("Análisis Categórico y Clasificación")
    st.markdown("Desglose de datos por etiquetas, estados y operadores.")

    # Obtener columnas categóricas (object/boolean)
    cols_cat = df_filtered.select_dtypes(include=['object', 'bool']).columns.tolist()

    if cols_cat:
        col_q1, col_q2 = st.columns(2)

        # 2.1 Tablas de Frecuencia Dinámicas
        with col_q1:
            st.subheader("Frecuencia por Categoría")
            cat_selected = st.selectbox("Elige una categoría para contar:", cols_cat, index=0)
            
            conteo = df_filtered[cat_selected].value_counts().reset_index()
            conteo.columns = [cat_selected, 'Conteo']
            
            # Mostrar tabla estilizada
            st.dataframe(conteo, use_container_width=True, hide_index=True)

        # 2.2 Tabla Cruzada (Pivot Table) Dinámica
        with col_q2:
            st.subheader("Tabla Cruzada (Crosstab)")
            st.markdown("Cruza dos variables cualitativas.")
            
            row_var = st.selectbox("Filas:", cols_cat, index=0, key='row_var')
            # Intentar seleccionar otra columna por defecto para las columnas
            idx_col = 1 if len(cols_cat) > 1 else 0
            col_var = st.selectbox("Columnas:", cols_cat, index=idx_col, key='col_var')
            
            if row_var and col_var:
                crosstab = pd.crosstab(df_filtered[row_var], df_filtered[col_var])
                st.dataframe(crosstab, use_container_width=True)

        st.divider()
        
        # 2.3 Modo "Insights" (Top Performers)
        st.subheader("🏆 Top Categorías")
        if 'Operador' in df_filtered.columns and 'Capacidad_Instalada_MW' in df_filtered.columns:
            top_op = df_filtered.groupby('Operador')['Capacidad_Instalada_MW'].sum().sort_values(ascending=False).head(3)
            st.write(f"**Operador con mayor capacidad:** {top_op.index[0]} ({top_op.values[0]:.2f} MW)")
    else:
        st.warning("No se encontraron columnas de texto/categóricas.")

# ==========================================
# PARTE 3: ANÁLISIS GRÁFICO
# ==========================================
with tab_graf:
    st.header("Visualización Interactiva")
    
    # Selector de Tipo de Gráfico
    chart_type = st.radio("Selecciona el tipo de visualización:", 
                          ["Distribución (Barras)", "Tendencia (Líneas)", "Relación (Dispersión)", "Proporción (Torta)"],
                          horizontal=True)

    # Contenedor dinámico para controles
    with st.container():
        c_g1, c_g2, c_g3 = st.columns(3)
        
        if chart_type == "Distribución (Barras)":
            with c_g1:
                x_axis = st.selectbox("Eje X (Categoría):", cols_cat)
            with c_g2:
                y_axis = st.selectbox("Eje Y (Numérico):", cols_num)
            with c_g3:
                color_by = st.selectbox("Color:", [None] + cols_cat)
            
            fig = px.bar(df_filtered, x=x_axis, y=y_axis, color=color_by, title=f"{y_axis} por {x_axis}")
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Tendencia (Líneas)":
            if 'Fecha_Entrada_Operacion' in df_filtered.columns:
                with c_g1:
                    y_axis_line = st.selectbox("Variable a medir en el tiempo:", cols_num, key='line_y')
                
                # Agrupación temporal automática
                df_time = df_filtered.sort_values('Fecha_Entrada_Operacion')
                fig = px.line(df_time, x='Fecha_Entrada_Operacion', y=y_axis_line, markers=True, title=f"Evolución de {y_axis_line}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No se encontró columna de fecha para hacer tendencias.")

        elif chart_type == "Relación (Dispersión)":
            with c_g1:
                scat_x = st.selectbox("Eje X:", cols_num, index=0)
            with c_g2:
                scat_y = st.selectbox("Eje Y:", cols_num, index=1 if len(cols_num)>1 else 0)
            with c_g3:
                scat_col = st.selectbox("Color por:", cols_cat)
            
            fig = px.scatter(df_filtered, x=scat_x, y=scat_y, color=scat_col, 
                             size='Capacidad_Instalada_MW' if 'Capacidad_Instalada_MW' in df_filtered.columns else None,
                             hover_data=df_filtered.columns,
                             title=f"Relación: {scat_x} vs {scat_y}")
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Proporción (Torta)":
            with c_g1:
                pie_names = st.selectbox("Categoría (Sectores):", cols_cat)
            with c_g2:
                pie_values = st.selectbox("Valores (Tamaño):", cols_num)
            
            fig = px.pie(df_filtered, names=pie_names, values=pie_values, title=f"Proporción de {pie_values} por {pie_names}")
            st.plotly_chart(fig, use_container_width=True)

# --- PIE DE PÁGINA ---
st.divider()
st.caption("Generado con Streamlit • Análisis de Datos Energéticos")
