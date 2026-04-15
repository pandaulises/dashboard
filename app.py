import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración base
st.set_page_config(page_title="Dashboard Profesional Almacén", layout="wide")

# URL Directa de descarga (Asegúrate de que no tenga espacios al final)
SHEET_ID = "18VER3KDvbMIIRXn76dsPqwlQWxAanulQCnDMWw54VDQ"
URL = f"https://google.com{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=300)
def cargar_datos_limpios():
    # Leemos con un timeout para evitar que se quede trabado
    df = pd.read_csv(URL)
    
    # 1. Limpiar nombres de columnas
    df.columns = [c.strip().lower() for c in df.columns]
    
    # 2. Rellenar VACÍOS con N/A
    df = df.fillna('N/A')
    
    # 3. Función para limpiar números complejos (como 1.089.731.981)
    def limpiar_numero(valor):
        if isinstance(valor, str):
            # Si tiene más de un punto, quitamos todos los puntos para que sea entero
            if valor.count('.') > 1:
                valor = valor.replace('.', '')
            else:
                # Si tiene comas, las quitamos
                valor = valor.replace(',', '')
        return pd.to_numeric(valor, errors='coerce')

    # Aplicar a columnas clave
    cols_num = ['precio', 'costo', 'salida pz', 'stock']
    for col in cols_num:
        if col in df.columns:
            df[col] = df[col].apply(limpiar_numero).fillna(0)
            
    return df

st.title("📊 Panel de Control de Almacén")

try:
    df = cargar_datos_limpios()

    # --- MÉTRICAS ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Gasto Total", f"${df['costo'].sum():,.2f}")
    with m2:
        st.metric("Piezas Entregadas", f"{int(df['salida pz'].sum()):,}")
    with m3:
        st.metric("Items en Stock", f"{int(df['stock'].sum()):,}")
    with m4:
        st.metric("Proveedores", df['proveedor'].nunique())

    st.markdown("---")

    # --- GRÁFICOS SOLICITADOS ---
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("💰 Gasto por Producto (Top 10)")
        gasto_prod = df.groupby('descripcion')['costo'].sum().nlargest(10).reset_index()
        fig1 = px.bar(gasto_prod, x='costo', y='descripcion', orientation='h', 
                      color='costo', color_continuous_scale='Blues')
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.subheader("👷 Consumo por Persona (Recibió)")
        consumo_pers = df.groupby('recibio')['costo'].sum().reset_index()
        fig2 = px.pie(consumo_pers, values='costo', names='recibio', hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🏗️ Análisis por Proyecto")
    proy_data = df.groupby('proyecto')['costo'].sum().reset_index()
    fig3 = px.bar(proy_data, x='proyecto', y='costo', color='proyecto')
    st.plotly_chart(fig3, use_container_width=True)

    # --- TABLA COMPLETA ---
    st.subheader("📋 Movimientos Detallados")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.info("Revisa que tu Google Sheet tenga el permiso: 'Cualquier persona con el enlace puede leer'.")

