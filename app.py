import streamlit as st
import pandas as pd
import plotly.express as px

# 1. DIRECCIÓN CORREGIDA (Sin espacios y formato directo)
SHEET_ID = "18VER3KDvbMIIRXn76dsPqwlQWxAanulQCnDMWw54VDQ"
# Forzamos el formato CSV limpio
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=60) # Bajamos el tiempo para probar rápido
def cargar_datos_limpios():
    # Usamos storage_options para evitar bloqueos de red simples
    df = pd.read_csv(URL, on_bad_lines='skip')
    
    # Limpiar nombres de columnas
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Rellenar VACÍOS con N/A
    df = df.fillna('N/A')
    
    # Función para limpiar números complejos (como 1.089.731.981)
    def limpiar_numero(valor):
        if isinstance(valor, str):
            # Limpieza total: solo dejamos dígitos y el último punto decimal si existe
            valor = valor.replace(',', '')
            if valor.count('.') > 1:
                valor = valor.replace('.', '')
        return pd.to_numeric(valor, errors='coerce')

    # Aplicar a columnas clave (Ajustadas a tus datos)
    cols_num = ['precio', 'costo', 'salida pz', 'stock']
    for col in cols_num:
        if col in df.columns:
            df[col] = df[col].apply(limpiar_numero).fillna(0)
            
    return df

# --- INTERFAZ ---
st.title("📊 Panel de Control de Almacén")

try:
    df = cargar_datos_limpios()
    
    # MÉTRICAS DINÁMICAS
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Gasto Total", f"${df['costo'].sum():,.2f}")
    with c2:
        st.metric("Piezas Entregadas", f"{int(df['salida pz'].sum()):,}")
    with c3:
        st.metric("Movimientos", len(df))

    # GRÁFICOS SOLICITADOS
    tab1, tab2 = st.tabs(["Análisis de Productos", "Consumo por Persona"])
    
    with tab1:
        st.subheader("💰 Top 10 Gasto por Artículo")
        top_prod = df.groupby('descripcion')['costo'].sum().nlargest(10).reset_index()
        fig1 = px.bar(top_prod, x='costo', y='descripcion', orientation='h', color='costo')
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        st.subheader("👷 Gasto Acumulado por Quién Recibe")
        recibe_df = df.groupby('recibio')['costo'].sum().reset_index()
        fig2 = px.pie(recibe_df, values='costo', names='recibio', hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📋 Base de Datos Completa")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.info("⚠️ Si el error persiste, dale a 'Reboot App' en el menú de la derecha.")
