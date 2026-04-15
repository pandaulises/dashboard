import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración base
st.set_page_config(page_title="Dashboard Profesional Almacén", layout="wide", initial_sidebar_state="collapsed")

# Estilo para fondo oscuro como el de tu imagen
st.markdown("<style>min-height: 100vh; background-color: #0e1117;</style>", unsafe_allow_html=True)

SHEET_ID = "18VER3KDvbMIIRXn76dsPqwlQWxAanulQCnDMWw54VDQ"
URL = f"https://google.com{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=300)
def cargar_datos_limpios():
    df = pd.read_csv(URL)
    
    # Limpiamos nombres de columnas (quitamos espacios y pasamos a minúsculas)
    df.columns = [c.strip().lower() for c in df.columns]
    
    # REGLA DE ESPACIOS VACÍOS: Llenar con N/A
    df = df.fillna('N/A')
    
    # LIMPIEZA DE NÚMEROS (Para que las métricas no den $0.00)
    # Esta función quita puntos de miles que confunden a Python
    def limpiar_numero(valor):
        if isinstance(valor, str):
            # Si el número tiene más de un punto (ej. 1.089.731), los quitamos todos
            if valor.count('.') > 1:
                valor = valor.replace('.', '')
            else:
                valor = valor.replace(',', '')
        return pd.to_numeric(valor, errors='coerce')

    # Aplicamos la limpieza a las columnas clave
    columnas_valor = ['precio', 'costo', 'salida pz', 'stock']
    for col in columnas_valor:
        if col in df.columns:
            df[col] = df[col].apply(limpiar_numero).fillna(0)
            
    return df

try:
    df = cargar_datos_limpios()

    # --- MÉTRICAS SUPERIORES ---
    m1, m2, m3, m4 = st.columns(4)
    # Usamos los nombres exactos de tus columnas
    with m1:
        total_gasto = df['costo'].sum()
        st.metric("Gasto Total", f"${total_gasto:,.2f}")
    with m2:
        total_pz = df['salida pz'].sum()
        st.metric("Piezas Entregadas", f"{int(total_pz):,}")
    with m3:
        total_stock = df['stock'].sum()
        st.metric("Items en Stock", f"{int(total_stock):,}")
    with m4:
        total_prov = df['proveedor'].nunique()
        st.metric("Proveedores", total_prov)

    st.markdown("---")

    # --- GRÁFICOS ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Distribución de Costos")
        # Filtramos N/A para que el gráfico sea limpio
        df_plot = df[df['proveedor'] != 'N/A']
        fig_costo = px.pie(df_plot, values='costo', names='proveedor', hole=0.4, 
                           color_discrete_sequence=px.colors.qualitative.Dark24)
        st.plotly_chart(fig_costo, use_container_width=True)

    with col2:
        st.subheader("🏗️ Consumo por Proyecto")
        # Agrupamos por proyecto y sumamos costo
        proy_df = df.groupby('proyecto')['costo'].sum().reset_index()
        fig_proy = px.bar(proy_df, x='proyecto', y='costo', color='costo',
                          text_auto='.2s', color_continuous_scale='YlGnBu')
        st.plotly_chart(fig_proy, use_container_width=True)

    # --- DETALLE DE MOVIMIENTOS ---
    st.subheader("📋 Detalle de Movimientos")
    busqueda = st.text_input("🔍 Buscar producto por descripción", "")
    
    if busqueda:
        df_final = df[df['descripcion'].str.contains(busqueda, case=False, na=False)]
    else:
        df_final = df

    st.dataframe(df_final, use_container_width=True)

except Exception as e:
    st.error(f"Error al procesar los datos: {e}")
    st.info("Asegúrate de que las columnas en tu Excel se llamen exactamente: Proyecto, Descripcion, Proveedor, Precio, Salida pz, Costo, Stock, Fecha, Recibio")
