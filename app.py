@st.cache_data(ttl=600)
def cargar_datos():
    # Leemos el CSV
    df = pd.read_csv(URL)
    
    # 1. Limpieza de nombres de columnas
    df.columns = [c.strip().lower() for c in df.columns]
    
    # 2. RELLENAR VACÍOS: Aquí está el truco
    # Esto busca celdas vacías en texto y pone 'N/A'
    df = df.fillna('N/A')
    
    # 3. Limpieza de números (aseguramos que sean 0 si están vacíos)
    for col in ['precio', 'costo', 'salida pz', 'stock']:
        if col in df.columns:
            # Convertimos a número, y lo que no sea número lo volvemos 0
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # 4. Limpieza de espacios extra en el texto
    # Esto quita espacios invisibles que a veces arruinan las gráficas
    df['proveedor'] = df['proveedor'].astype(str).str.strip()
    df['descripcion'] = df['descripcion'].astype(str).str.strip()
    
    # 5. Convertir fecha
    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'], dayfirst=True, errors='coerce')
        
    return df
