import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard Energía Renovable",
    page_icon="⚡",
    layout="wide"
)

# --- TÍTULO ---
st.title("⚡ Análisis Exploratorio de Energía Renovable")

# --- BARRA LATERAL: CARGA DE ARCHIVOS ---
st.sidebar.header("📂 Configuración")
st.sidebar.markdown("Sube tu archivo CSV para analizar.")

uploaded_file = st.sidebar.file_uploader("Cargar dataset (.csv)", type=["csv"])

# Variable para almacenar el dataframe
df = None

# --- LÓGICA DE CARGA Y MANEJO DE ERRORES ---
if uploaded_file is not None:
    try:
        # Intentamos leer el archivo
        df = pd.read_csv(uploaded_file)
        
        # Validación básica: Verificar si existen columnas críticas
        required_columns = ['Fecha_Entrada_Operacion', 'Tecnologia', 'Operador', 'Capacidad_Instalada_MW']
        if not all(col in df.columns for col in required_columns):
            st.error("❌ El archivo no tiene el formato correcto. Faltan columnas clave (ej. Fecha_Entrada_Operacion, Tecnologia).")
            st.stop()

        # Convertir fecha a datetime
        df['Fecha_Entrada_Operacion'] = pd.to_datetime(df['Fecha_Entrada_Operacion'])
        
        st.sidebar.success("✅ Archivo cargado correctamente")

    except Exception as e:
        st.error(f"❌ Ocurrió un error al procesar el archivo: {e}")
        st.info("Por favor, verifica que el archivo sea un CSV válido e inténtalo de nuevo.")
        st.stop()
else:
    # MENSAJE DE BIENVENIDA (ESTADO VACÍO)
    st.info("👋 **Bienvenido!** Para comenzar, por favor sube un archivo CSV en el panel de la izquierda.")
    st.markdown("""
        **Formato esperado del CSV:**
        Debe contener columnas como:
        * `Tecnologia`
        * `Operador`
        * `Capacidad_Instalada_MW`
        * `Fecha_Entrada_Operacion`
        * `Estado_Actual`
    """)
    st.stop() # Detiene la ejecución aquí hasta que haya archivo

# --- A PARTIR DE AQUÍ SOLO SE EJECUTA SI EL ARCHIVO CARGÓ BIEN ---

# --- SIDEBAR (FILTROS) ---
st.sidebar.divider()
st.sidebar.header("🔍 Filtros")

# Filtro por Tecnología
tecnologias = df['Tecnologia'].unique()
tech_filter = st.sidebar.multiselect("Seleccionar Tecnología", tecnologias, default=tecnologias)

# Filtro por Operador
operadores = df['Operador'].unique()
op_filter = st.sidebar.multiselect("Seleccionar Operador", operadores, default=operadores)

# Filtro por Estado
if 'Estado_Actual' in df.columns:
    estados = df['Estado_Actual'].unique()
    status_filter = st.sidebar.multiselect("Estado del Proyecto", estados, default=estados)
    
    # Aplicar filtros
    df_filtered = df[
        (df['Tecnologia'].isin(tech_filter)) & 
        (df['Operador'].isin(op_filter)) & 
        (df['Estado_Actual'].isin(status_filter))
    ]
else:
    # Fallback si no existe la columna Estado
    df_filtered = df[
        (df['Tecnologia'].isin(tech_filter)) & 
        (df['Operador'].isin(op_filter))
    ]

# --- VERIFICAR SI LOS FILTROS DEJARON DATOS VACÍOS ---
if df_filtered.empty:
    st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados.")
    st.stop()

# --- MÉTRICAS PRINCIPALES (KPIs) ---
st.markdown("### 📊 Métricas Generales")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Proyectos", df_filtered.shape[0])
with col2:
    if 'Capacidad_Instalada_MW' in df_filtered.columns:
        total_mw = df_filtered['Capacidad_Instalada_MW'].sum()
        st.metric("Capacidad Total (MW)", f"{total_mw:,.2f}")
with col3:
    if 'Eficiencia_Planta_Pct' in df_filtered.columns:
        avg_eff = df_filtered['Eficiencia_Planta_Pct'].mean()
        st.metric("Eficiencia Promedio", f"{avg_eff:.1f}%")
with col4:
    if 'Inversion_Inicial_MUSD' in df_filtered.columns:
        total_inv = df_filtered['Inversion_Inicial_MUSD'].sum()
        st.metric("Inversión Total (MUSD)", f"${total_inv:,.2f}")

st.divider()

# --- PESTAÑAS DE ANÁLISIS ---
tab1, tab2, tab3, tab4 = st.tabs(["🏭 Distribución", "📈 Rendimiento", "💰 Económico", "📅 Línea de Tiempo"])

# TAB 1: Distribución de Proyectos
with tab1:
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.subheader("Proyectos por Tecnología")
        conteo_tech = df_filtered['Tecnologia'].value_counts().reset_index()
        conteo_tech.columns = ['Tecnologia', 'Cantidad']
        fig_bar = px.bar(conteo_tech, x='Tecnologia', y='Cantidad', color='Tecnologia', 
                            text='Cantidad', template="plotly_white")
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_t2:
        st.subheader("Participación por Operador")
        fig_pie = px.pie(df_filtered, names='Operador', values='Capacidad_Instalada_MW', 
                            title='Capacidad (MW) por Operador', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

# TAB 2: Relación Técnica (Scatter Plots)
with tab2:
    st.subheader("Relación Capacidad Instalada vs. Generación Diaria")
    if 'Generacion_Diaria_MWh' in df_filtered.columns:
        fig_scatter = px.scatter(
            df_filtered, 
            x='Capacidad_Instalada_MW', 
            y='Generacion_Diaria_MWh', 
            color='Tecnologia',
            size='Eficiencia_Planta_Pct' if 'Eficiencia_Planta_Pct' in df_filtered.columns else None,
            hover_data=['Operador'],
            template="plotly_dark",
            title="Capacidad vs Generación"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Datos de generación diaria no disponibles.")

# TAB 3: Análisis Económico
with tab3:
    col_e1, col_e2 = st.columns(2)
    
    with col_e1:
        if 'Inversion_Inicial_MUSD' in df_filtered.columns:
            st.subheader("Distribución de Inversión por Tecnología")
            fig_box = px.box(df_filtered, x='Tecnologia', y='Inversion_Inicial_MUSD', color='Tecnologia',
                                points="all", title="Rango de Inversión (MUSD)")
            st.plotly_chart(fig_box, use_container_width=True)
        
    with col_e2:
        if 'Estado_Actual' in df_filtered.columns:
            st.subheader("Estado Actual de los Proyectos")
            estado_counts = df_filtered['Estado_Actual'].value_counts().reset_index()
            estado_counts.columns = ['Estado', 'Cantidad']
            fig_status = px.bar(estado_counts, x='Cantidad', y='Estado', orientation='h', 
                                color='Estado', title="Conteo por Estado del Proyecto")
            st.plotly_chart(fig_status, use_container_width=True)

# TAB 4: Serie de Tiempo
with tab4:
    st.subheader("Entrada en Operación a lo largo del tiempo")
    
    # Agrupar por año-mes
    timeline = df_filtered.set_index('Fecha_Entrada_Operacion').resample('M')['Capacidad_Instalada_MW'].sum().reset_index()
    timeline['Capacidad_Acumulada'] = timeline['Capacidad_Instalada_MW'].cumsum()
    
    fig_line = px.line(timeline, x='Fecha_Entrada_Operacion', y='Capacidad_Acumulada', 
                        markers=True, title="Crecimiento de Capacidad Instalada Acumulada (MW)")
    st.plotly_chart(fig_line, use_container_width=True)

# --- DATOS CRUDOS ---
with st.expander("Ver Datos Crudos"):
    st.dataframe(df_filtered)
