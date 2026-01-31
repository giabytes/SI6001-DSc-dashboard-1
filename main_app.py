import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- CONFIGURACIÓN DE LA PÁGINA: ¡Súper cute! ---
st.set_page_config(
    page_title="💖 Mi Dash de Datos Estilo Pastel 🎀",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS PERSONALIZADOS: ¡Para que brille! ---
st.markdown("""
    <style>
    /* Fondo de la app */
    .stApp {
        background-color: #FFF0F5; /* Pink claro */
        color: #5D5C61; /* Gris suave */
    }
    /* Estilo del título principal */
    h1 {
        color: #FF69B4; /* Hot Pink */
        text-align: center;
        font-family: 'Georgia', serif;
        font-weight: bold;
    }
    /* Subtítulos */
    h2, h3 {
        color: #FFB6C1; /* Light Pink */
        font-family: 'Arial', sans-serif;
    }
    /* Texto normal y markdown */
    p, .stMarkdown {
        color: #8D8C94; /* Gris intermedio */
        font-family: 'Arial', sans-serif;
    }
    /* Sidebar */
    .stSidebar {
        background-color: #F8F8FF; /* Ghost White */
        border-right: 1px solid #FFDAB9; /* Peach Puff */
    }
    .stSidebar h1, .stSidebar h2, .stSidebar h3 {
        color: #FFC0CB; /* Pink */
    }
    /* Botones y selectores */
    .stButton>button {
        background-color: #FFDAB9; /* Peach Puff */
        color: #5D5C61;
        border-radius: 8px;
        border: 1px solid #FFC0CB;
    }
    .stButton>button:hover {
        background-color: #FFC0CB; /* Pink */
        color: white;
    }
    .stSelectbox, .stMultiSelect, .stSlider {
        background-color: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #E6E6FA; /* Lavender */
    }
    /* Métricas */
    div.stMetric {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #FFD1DC; /* Pink Light */
    }
    .stMetric label {
        color: #FF69B4 !important; /* Hot Pink */
        font-weight: bold;
    }
    .stMetric .css-1b3c3lz { /* Value */
        color: #F08080 !important; /* Light Coral */
    }
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #FFD1DC; /* Pink Light */
        color: #FF69B4; /* Hot Pink */
        border-radius: 8px;
        padding: 10px;
    }
    .streamlit-expanderContent {
        background-color: #F8F8FF; /* Ghost White */
        border-bottom-left-radius: 8px;
        border-bottom-right-radius: 8px;
        border: 1px solid #FFD1DC;
        border-top: none;
    }
    /* Mensajes de info/warning/error */
    .stAlert.info {
        background-color: #E0FFFF; /* Light Cyan */
        color: #4682B4; /* Steel Blue */
        border-radius: 8px;
    }
    .stAlert.warning {
        background-color: #FFFACD; /* Lemon Chiffon */
        color: #DAA520; /* Goldenrod */
        border-radius: 8px;
    }
    .stAlert.error {
        background-color: #FFC0CB; /* Pink */
        color: #8B0000; /* Dark Red */
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💖 Mi Dash de Datos Estilo Pastel 🎀")
st.markdown("¡Prepárate para deslumbrarte! Sube cualquier CSV y vamos a analizarlo con un toque *girly* y muchos brillos. ✨")

# --- BARRA LATERAL: ¡Para que todo fluya! ---
st.sidebar.header("🌸 Sube tu Magia CSV")
uploaded_file = st.sidebar.file_uploader("Arrastra tu archivo aquí, ¡o haz click para buscarlo!", type=["csv"])

if uploaded_file is not None:
    try:
        # Cargando los datos, ¡con cariño!
        df_raw = pd.read_csv(uploaded_file)
        total_filas = len(df_raw)

        st.sidebar.divider()
        st.sidebar.header("📏 Cuántos registros analizamos?")
        
        # Slider para elegir la cantidad de registros, ¡súper intuitivo!
        cantidad = st.sidebar.slider(
            "Desliza para elegir cuántas filas quieres explorar:",
            min_value=1,
            max_value=total_filas,
            value=min(200, total_filas), # Valor por defecto, ¡para empezar rápido!
            help="¡Demasiados datos pueden ser abrumadores! Elige una porción perfecta."
        )
        
        # Aplicamos el recorte de datos, ¡solo lo esencial!
        df = df_raw.head(cantidad).copy()
        st.sidebar.info(f"✨ ¡Analizando los primeros **{cantidad}** de **{total_filas}** registros! ¡Qué emocionante!")

        # --- DETECCIÓN AUTOMÁTICA DE TIPOS: ¡La IA trabajando para ti! ---
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    # Intentamos que sea una fecha, ¡por si acaso!
                    df[col] = pd.to_datetime(df[col], errors='coerce') 
                except:
                    pass # Si no es fecha, ¡no pasa nada!

        cols_num = df.select_dtypes(include=[np.number]).columns.tolist()
        cols_cat = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
        cols_date = df.select_dtypes(include=['datetime64[ns]']).columns.tolist() # ¡Importante el [ns]!

        st.sidebar.divider()
        st.sidebar.subheader("🌟 Filtros Mágicos")
        if cols_cat:
            cat_to_filter = st.sidebar.selectbox("Filtrar por esta categoría:", ["Ninguno"] + cols_cat)
            if cat_to_filter != "Ninguno":
                val_filter = st.sidebar.multiselect(f"Selecciona los valores de {cat_to_filter}", df[cat_to_filter].unique())
                if val_filter:
                    df = df[df[cat_to_filter].isin(val_filter)]
                else:
                    st.sidebar.warning(f"¡Oops! Necesitas seleccionar al menos un valor para {cat_to_filter}.")
        
        # Si no quedan datos después de los filtros... ¡ups!
        if df.empty:
            st.warning("💔 ¡No hay datos que coincidan con tus filtros! Intenta con otras opciones.")
            st.stop()


        # --- PESTAÑAS DE ANÁLISIS: ¡Organizado y chic! ---
        tab_cuant, tab_cual, tab_graf = st.tabs([
            "🔢 Cuantitativo: ¡Números que hablan!", 
            "📝 Cualitativo: ¡Categorías cool!", 
            "📊 Gráfico: ¡Visualiza tus sueños!"
        ])

        # ==========================================
        # 1. ANÁLISIS CUANTITATIVO (NÚMEROS)
        # ==========================================
        with tab_cuant:
            st.header("✨ Números con Encanto ✨")
            st.markdown("¡Aquí es donde las cifras toman protagonismo! Descubre el corazón numérico de tus datos.")
            
            if cols_num:
                st.subheader("🌸 El Resumen Glamuroso")
                st.dataframe(df.describe().T, use_container_width=True)
                
                st.divider()
                st.subheader("💖 ¡Correlaciones que Enamoran!")
                st.markdown("¿Qué variables se llevan bien? Descubre sus conexiones secretas.")
                if len(cols_num) > 1:
                    # Usamos una escala de color más girly
                    fig_corr = px.imshow(df[cols_num].corr(), text_auto=True, color_continuous_scale=px.colors.sequential.RdPu)
                    st.plotly_chart(fig_corr, use_container_width=True)
                else:
                    st.info("¡Necesitas al menos dos columnas numéricas para ver las correlaciones, cariño!")
            else:
                st.warning("¡Ay no! No encontramos columnas numéricas en tu dataset. 😥")

        # ==========================================
        # 2. ANÁLISIS CUALITATIVO (CATEGORÍAS)
        # ==========================================
        with tab_cual:
            st.header("🎀 Categorías con Estilo 🎀")
            st.markdown("Explora cómo tus datos se agrupan en diferentes categorías. ¡Es como clasificar tus accesorios!")
            
            if cols_cat:
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("🌸 ¿Cuántos de Cada Uno?")
                    target_cat = st.selectbox("Elige la categoría que quieres contar:", cols_cat, key='cual_count_select')
                    st.table(df[target_cat].value_counts().reset_index().rename(columns={'index': target_cat, target_cat: 'Conteo'}))
                with c2:
                    if len(cols_cat) > 1:
                        st.subheader("💖 ¡Cruce de Categorías para Descubrir!")
                        st.markdown("Descubre patrones al cruzar dos categorías. ¡Súper insight!")
                        c_row = st.selectbox("Filas (como tu base):", cols_cat, index=0, key='cual_crosstab_row')
                        # Asegurar que no sea la misma columna si es posible
                        idx_col = 1 if len(cols_cat) > 1 and cols_cat[0] == c_row else 0
                        if len(cols_cat) > idx_col:
                            if cols_cat[idx_col] == c_row and len(cols_cat) > idx_col +1:
                                idx_col += 1
                            elif cols_cat[idx_col] == c_row and len(cols_cat) == 1:
                                idx_col = 0 # solo hay una columna
                            elif cols_cat[idx_col] == c_row: # Si es la misma y no hay mas columnas
                                pass
                        
                        c_col = st.selectbox("Columnas (como tu *statement*):", cols_cat, index=idx_col, key='cual_crosstab_col')
                        
                        if c_row == c_col:
                             st.warning("¡Uhm, elige dos categorías diferentes para cruzar, linda!")
                        else:
                            st.dataframe(pd.crosstab(df[c_row], df[c_col]), use_container_width=True)
                    else:
                        st.info("¡Necesitas al menos dos categorías para hacer un cruce, amiga!")
            else:
                st.warning("¡No hay columnas categóricas para explorar! Intenta con un dataset diferente. 😔")

        # ==========================================
        # 3. ANÁLISIS GRÁFICO (EXPLORACIÓN)
        # ==========================================
        with tab_graf:
            st.header("🌈 ¡Visualiza tus Sueños en Gráficos! 🌈")
            st.markdown("¡Da vida a tus datos con estos gráficos preciosos y personalizables!")
            
            # Selector de tipo de gráfico, ¡elige tu favorito!
            tipo_g = st.radio(
                "¿Qué tipo de gráfico te apetece hoy?", 
                ["Barras: ¡Comparaciones top!", "Dispersión: ¡Relaciones secretas!", "Líneas: ¡Tendencias que marcan!", "Caja: ¡Descubre la distribución!"],
                horizontal=True
            )
            
            # Asegurarse de tener opciones para los selectores
            all_cols = cols_num + cols_cat + cols_date
            if not all_cols:
                st.warning("¡No hay columnas para graficar! Sube un dataset completo. 😞")
                st.stop()

            # Columnas para los selectores de ejes
            c_graph1, c_graph2, c_graph3 = st.columns(3)
            
            with c_graph1:
                gx = st.selectbox("Eje X (¿Qué quieres ver abajo?):", all_cols, key='graph_x')
            with c_graph2:
                # Eje Y: preferiblemente numérico, pero si no hay, acepta otros
                gy_options = cols_num if cols_num else all_cols
                gy = st.selectbox("Eje Y (¿Qué quieres ver arriba?):", gy_options, key='graph_y')
            with c_graph3:
                # Color: preferiblemente categórico, pero si no hay, acepta otros
                gcol_options = ["Ninguno"] + cols_cat if cols_cat else ["Ninguno"] + all_cols
                gcol = st.selectbox("Color por (¡Dale un toque especial!):", gcol_options, key='graph_color')
            
            color_param = gcol if gcol != "Ninguno" else None

            # Generación de los gráficos, ¡con un estilo pastel!
            if tipo_g == "Barras: ¡Comparaciones top!":
                if gx and gy:
                    fig = px.bar(df, x=gx, y=gy, color=color_param, barmode="group",
                                 title=f"Gráfico de Barras: {gy} vs {gx}",
                                 color_discrete_sequence=px.colors.sequential.RdPu)
                else:
                    st.warning("¡Selecciona Eje X y Eje Y para tu gráfico de barras, hermosa!")
            
            elif tipo_g == "Dispersión: ¡Relaciones secretas!":
                if gx and gy:
                    fig = px.scatter(df, x=gx, y=gy, color=color_param,
                                     title=f"Gráfico de Dispersión: {gy} vs {gx}",
                                     color_discrete_sequence=px.colors.qualitative.Pastel)
                else:
                    st.warning("¡Necesitas Eje X y Eje Y para ver la relación en tu gráfico de dispersión!")

            elif tipo_g == "Líneas: ¡Tendencias que marcan!":
                if gx and gy:
                    fig = px.line(df, x=gx, y=gy, color=color_param, markers=True,
                                  title=f"Gráfico de Líneas: {gy} en el tiempo de {gx}",
                                  color_discrete_sequence=px.colors.qualitative.Pastel2)
                else:
                    st.warning("¡Define Eje X y Eje Y para tu gráfico de líneas!")

            elif tipo_g == "Caja: ¡Descubre la distribución!":
                if gy and gx: # En la caja, gx es la categoría y gy es el valor numérico
                    fig = px.box(df, x=gx, y=gy, color=color_param,
                                 title=f"Gráfico de Caja: Distribución de {gy} por {gx}",
                                 color_discrete_sequence=px.colors.qualitative.T10)
                else:
                    st.warning("¡Selecciona una categoría (Eje X) y un valor numérico (Eje Y) para el gráfico de caja!")

            if 'fig' in locals(): # Asegurarse de que la figura se creó
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("¡Selecciona tus opciones para ver el gráfico aparecer aquí! 🤩")

    except Exception as e:
        st.error(f"💔 ¡Ups! Hubo un problema procesando tu archivo: **{e}**")
        st.info("¡Asegúrate de que sea un CSV válido y vuelve a intentarlo, corazón! Puedes cerrar y abrir de nuevo el navegador para un *fresh start*.")
        if st.button("Reintentar con un archivo diferente"):
            st.rerun() # Reinicia la app para subir otro archivo

else:
    st.info("🌟 ¡Bienvenida! Sube un archivo CSV en la barra lateral izquierda para que la magia comience. ¡Es súper fácil!")
    st.markdown("""
        <div style="text-align: center;">
            <p style="color: #FFC0CB; font-size: 1.2em;">
                ¡Imagina tu reporte más <span style="font-weight: bold;">girly</span>!
            </p>
        </div>
        """, unsafe_allow_html=True)

# --- PIE DE PÁGINA: ¡Siempre con estilo! ---
st.divider()
st.caption("💕 Diseñado con 💖 y Streamlit • ¡Porque los datos también pueden ser adorables!")
