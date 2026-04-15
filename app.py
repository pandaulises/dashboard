import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración profesional de la página
st.set_page_config(page_title="Dashboard Inventario Real-Time", layout="wide")

# URL de tu Google Sheet (Link de compartir)
SHEET_URL = "https://docs.google.com/spreadsheets/d/18VER3KDvbMIIRXn76dsPqwlQWxAanulQCnDMWw54VDQ/edit?usp=sharing"

@st.cache_data(ttl=600) # Se actualiza cada 10 minutos
def load_data_from_gsheets(url):
    # Transformamos el link de edición a link de descarga CSV
    csv_url = url.replace('/edit?usp=sharing', '/export?format=csv')
    df = pd.read_csv(csv_url)
    
    # Limpieza básica de columnas
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
    
    # Convertir fecha a formato datetime
    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'], dayfirst=True, errors='coerce')
    
    # Limpieza de precios (quitar puntos de miles si existen y convertir a numérico)
    for col in ['precio', 'costo', 'salida_pz']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df

st.title("📊 Dashboard de Control de Almacén")
st.info(f"Conectado a: [Google Sheet Original]({SHEET_URL})")

try:
    df = load_data_from_gsheets(SHEET_URL)

    # --- MÉTRICAS PRINCIPALES ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Inversión Total", f"${df['costo'].sum():,.2f}")
    with m2:
        st.metric("Pz Entregadas", f"{df['salida_pz'].sum():,.0f}")
    with m3:
        st.metric("Ítem más solicitado", df['descripcion'].mode()[0])
    with m4:
        st.metric("Proveedores", df['proveedor'].nunique())

    st.markdown("---")

    # --- GRÁFICOS ---
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Distribución de Gastos por Proveedor")
        fig_pie = px.sunburst(df, path=['proveedor', 'descripcion'], values='costo',
                             color='costo', color_continuous_scale='RdBu')
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        st.subheader("Consumo de Diesel vs Otros (Costo)")
        # Agrupamos por descripción para ver quién se lleva el presupuesto
        top_gastos = df.groupby('descripcion')['costo'].sum().nlargest(10).reset_index()
        fig_bar = px.bar(top_gastos, x='costo', y='descripcion', orientation='h', 
                         text_auto='.2s', color='costo')
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- LÍNEA DE TIEMPO ---
    st.subheader("Tendencia de Salidas por Fecha")
    timeline = df.groupby('fecha')['costo'].sum().reset_index()
    fig_line = px.area(timeline, x='fecha', y='costo', title="Gasto Diario Acumulado")
    st.plotly_chart(fig_line, use_container_width=True)

    # --- TABLA INTERACTIVA ---
    st.subheader("📦 Detalle de Movimientos")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error("No se pudo conectar con el archivo. Asegúrate de que el link tenga permiso de 'Cualquier persona con el enlace puede leer'.")
    st.write(e)
