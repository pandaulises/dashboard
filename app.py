import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página (Debe ir al principio)
st.set_page_config(page_title="Dashboard de Inventario", layout="wide", page_icon="📊")

# 2. Configuración de la fuente de datos (URL CORREGIDA)
SHEET_ID = "18VER3KDvbMIIRXn76dsPqwlQWxAanulQCnDMWw54VDQ"
# La URL debe incluir /spreadsheets/d/ para que funcione
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=600)
def cargar_datos():
    # Leer el CSV desde Google Sheets
    df = pd.read_csv(URL)
    
    # Limpiar nombres de columnas: quitar espacios y minúsculas
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Rellenar celdas vacías para evitar errores en gráficos
    df = df.fillna('N/A')
    
    # Limpiar columnas numéricas (convertir a 0 si hay error o está vacío)
    # Ajusté los nombres para que coincidan con lo que suele haber en un Sheet
    columnas_num = ['precio', 'costo', 'salida pz', 'stock']
    for col in columnas_num:
        if col in df.columns:
            # Quitamos símbolos de moneda o comas si existen antes de convertir
            if df[col].dtype == 'object':
                df[col] = df[col].str.replace('$', '').str.replace(',', '')
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    # Limpiar espacios en blanco en textos
    columnas_texto = ['proyecto', 'descripcion', 'proveedor', 'recibio']
    for col in columnas_texto:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    # Convertir fecha de forma segura
    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'], dayfirst=True, errors='coerce')
        
    return df

# --- INTERFAZ DEL DASHBOARD ---
st.title("📊 Panel de Control de Almacén")
st.markdown("---")

try:
    data = cargar_datos()

    # MÉTRICAS PRINCIPALES (Usando nombres de columnas limpios)
    m1, m2, m3, m4 = st.columns(4)
    
    # Verificamos que las columnas existan antes de calcular
    costo_total = data['costo'].sum() if 'costo' in data.columns else 0
    salidas = data['salida pz'].sum() if 'salida pz' in data.columns else 0
    stock_total = data['stock'].sum() if 'stock' in data.columns else 0
    prov_count = data['proveedor'].nunique() if 'proveedor' in data.columns else 0

    with m1:
        st.metric("Gasto Total", f"${costo_total:,.2f}")
    with m2:
        st.metric("Piezas Entregadas", f"{int(salidas):,}")
    with m3:
        st.metric("Ítems en Stock", f"{int(stock_total):,}")
    with m4:
        st.metric("Proveedores", prov_count)

    st.markdown("---")

    # GRÁFICOS
    col_izq, col_der = st.columns(2)

    with col_izq:
        st.subheader("💰 Distribución de Costos")
        if 'proveedor' in data.columns and 'descripcion' in data.columns:
            fig_sun = px.sunburst(data, path=['proveedor', 'descripcion'], values='costo',
                                  color='costo', color_continuous_scale='Blues')
            st.plotly_chart(fig_sun, use_container_width=True)
        else:
            st.info("Faltan columnas 'proveedor' o 'descripcion' para el gráfico.")

    with col_der:
        st.subheader("🏗️ Consumo por Proyecto")
        if 'proyecto' in data.columns:
            proy_data = data.groupby('proyecto')['costo'].sum().reset_index()
            fig_bar = px.bar(proy_data, x='proyecto', y='costo', color='costo', 
                             text_auto='.2s', color_continuous_scale='Viridis')
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Falta la columna 'proyecto' para el gráfico.")

    # TABLA DE DATOS
    st.subheader("📋 Detalle de Movimientos")
    busqueda = st.text_input("🔍 Buscar producto por descripción:")
    
    if busqueda and 'descripcion' in data.columns:
        df_mostrar = data[data['descripcion'].str.contains(busqueda, case=False)]
    else:
        df_mostrar = data
        
    st.dataframe(df_mostrar, use_container_width=True)

except Exception as e:
    st.error("🚨 Error crítico al cargar los datos.")
    st.info("Asegúrate de que en Google Sheets hayas ido a 'Compartir' -> 'Cualquier persona con el enlace' -> 'Lector'.")
    st.write(f"**Detalle técnico:** {e}")

# Botón de refresco en la barra lateral
if st.sidebar.button('🔄 Forzar Actualización'):
    st.cache_data.clear()
    st.rerun()
