import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard Energía Renovable",
    page_icon="⚡",
    layout="wide"
)

# --- FUNCIÓN DE CARGA DE DATOS ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('energia_renovable.csv')
        # Convertir fecha a datetime
        df['Fecha_Entrada_Operacion'] = pd.to_datetime(df['Fecha_Entrada_Operacion'])
        return df
    except FileNotFoundError:
        st.error("El archivo 'energia_renovable.csv' no se encontró. Asegúrate de que esté en la misma carpeta.")
        return pd.DataFrame()

df = load_data()

# --- TÍTULO Y DESCRIPCIÓN ---
st.title("⚡ Análisis Exploratorio de Energía Renovable")
st.markdown("""
Este dashboard permite explorar interactivamente los datos de proyectos de energía renovable, 
analizando capacidades, inversiones, eficiencia y distribución por operadores.
""")

if not df.empty:
    # --- SIDEBAR (FILTROS) ---
    st.sidebar.header("🔍 Filtros")
    
    # Filtro por Tecnología
    tecnologias = df['Tecnologia'].unique()
    tech_filter = st.sidebar.multiselect("Seleccionar Tecnología", tecnologias, default=tecnologias)
    
    # Filtro por Operador
    operadores = df['Operador'].unique()
    op_filter = st.sidebar.multiselect("Seleccionar Operador", operadores, default=operadores)
    
    # Filtro por Estado
    estados = df['Estado_Actual'].unique()
    status_filter = st.sidebar.multiselect("Estado del Proyecto", estados, default=estados)

    # Aplicar filtros
    df_filtered = df[
        (df['Tecnologia'].isin(tech_filter)) & 
        (df['Operador'].isin(op_filter)) & 
        (df['Estado_Actual'].isin(status_filter))
    ]

    # --- MÉTRICAS PRINCIPALES (KPIs) ---
    st.markdown("### 📊 Métricas Generales")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Proyectos", df_filtered.shape[0])
    with col2:
        total_mw = df_filtered['Capacidad_Instalada_MW'].sum()
        st.metric("Capacidad Total (MW)", f"{total_mw:,.2f}")
    with col3:
        avg_eff = df_filtered['Eficiencia_Planta_Pct'].mean()
        st.metric("Eficiencia Promedio", f"{avg_eff:.1f}%")
    with col4:
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
        st.markdown("Analiza si las plantas más grandes son necesariamente las que más generan.")
        
        fig_scatter = px.scatter(
            df_filtered, 
            x='Capacidad_Instalada_MW', 
            y='Generacion_Diaria_MWh', 
            color='Tecnologia',
            size='Eficiencia_Planta_Pct',
            hover_data=['Operador', 'Estado_Actual'],
            template="plotly_dark",
            title="Capacidad vs Generación (Tamaño = Eficiencia)"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # TAB 3: Análisis Económico
    with tab3:
        col_e1, col_e2 = st.columns(2)
        
        with col_e1:
            st.subheader("Distribución de Inversión por Tecnología")
            fig_box = px.box(df_filtered, x='Tecnologia', y='Inversion_Inicial_MUSD', color='Tecnologia',
                             points="all", title="Rango de Inversión (MUSD)")
            st.plotly_chart(fig_box, use_container_width=True)
            
        with col_e2:
            st.subheader("Estado Actual de los Proyectos")
            # Agrupar datos para gráfico de barras apiladas o simple
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

else:
    st.warning("Esperando datos...")
