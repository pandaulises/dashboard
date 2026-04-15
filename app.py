import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página (Debe ir al principio)
st.set_page_config(page_title="Dashboard de Inventario", layout="wide")

# 2. Configuración de la fuente de datos
SHEET_ID = "18VER3KDvbMIIRXn76dsPqwlQWxAanulQCnDMWw54VDQ"
URL = f"https://google.com{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=600)
def cargar_datos():
    # Leer el CSV desde Google Sheets
    df = pd.read_csv(URL)
    
    # Limpiar nombres de columnas (quitar espacios y poner minúsculas)
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Rellenar celdas vacías con "N/A" para que los gráficos no fallen
    df = df.fillna('N/A')
    
    # Limpiar columnas numéricas (convertir a 0 si hay error o está vacío)
    columnas_num = ['precio', 'costo', 'salida pz', 'stock']
    for col in columnas_num:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    # Limpiar espacios en blanco en textos de categorías
    for col in ['proyecto', 'descripcion', 'proveedor', 'recibio']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    # Convertir fecha
    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'], dayfirst=True, errors='coerce')
        
    return df

# --- INTERFAZ DEL DASHBOARD ---
st.title("📊 Panel de Control de Almacén")
st.markdown("---")

try:
    data = cargar_datos()

    # MÉTRICAS PRINCIPALES
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Gasto Total", f"${data['costo'].sum():,.2f}")
    with m2:
        st.metric("Piezas Entregadas", f"{int(data['salida pz'].sum()):,}")
    with m3:
        st.metric("Ítems en Stock", f"{int(data['stock'].sum()):,}")
    with m4:
        st.metric("Proveedores", data['proveedor'].nunique())

    st.markdown("---")

    # GRÁFICOS
    col_izq, col_der = st.columns(2)

    with col_izq:
        st.subheader("💰 Distribución de Costos")
        # Gráfico Sunburst: Proveedor -> Descripción
        fig_sun = px.sunburst(data, path=['proveedor', 'descripcion'], values='costo',
                              color='costo', color_continuous_scale='Blues')
        st.plotly_chart(fig_sun, use_container_width=True)

    with col_der:
        st.subheader("🏗️ Consumo por Proyecto")
        # Gráfico de barras por proyecto
        proy_data = data.groupby('proyecto')['costo'].sum().reset_index()
        fig_bar = px.bar(proy_data, x='proyecto', y='costo', color='costo', 
                         text_auto='.2s', color_continuous_scale='Viridis')
        st.plotly_chart(fig_bar, use_container_width=True)

    # TABLA DE DATOS
    st.subheader("📋 Detalle de Movimientos")
    # Filtro rápido por descripción
    busqueda = st.text_input("Buscar producto:")
    if busqueda:
        df_mostrar = data[data['descripcion'].str.contains(busqueda, case=False)]
    else:
        df_mostrar = data
        
    st.dataframe(df_mostrar, use_container_width=True)

except Exception as e:
    st.error("Hubo un problema al cargar los datos. Revisa que el Google Sheet sea público.")
    st.write(f"Detalle del error: {e}")
