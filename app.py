import streamlit as st
import PyPDF2
import re
import pandas as pd
from datetime import datetime
import os

# CONFIGURACIÓN DE ALTO NIVEL
st.set_page_config(page_title="OBITER - Intelligence Unit", layout="wide")

# ARCHIVO DE PERSISTENCIA (Tu Equifax privado)
DB_FILE = "obiter_intelligence.csv"

# Cargar base de datos existente o crear una nueva
if os.path.exists(DB_FILE):
    st.session_state['obiter_db'] = pd.read_csv(DB_FILE).to_dict('records')
elif 'obiter_db' not in st.session_state:
    st.session_state['obiter_db'] = []

def extraer_dna_legal(texto, nombre_archivo):
    # Extracción de fechas y cálculo de inactividad
    fechas = re.findall(r'\d{2}/\d{2}/\d{4}', texto)
    meses_inactivo = 0
    ultima_fecha_str = "S/D"
    
    if fechas:
        lista_fechas = []
        for f in fechas:
            try:
                d = datetime.strptime(f, '%d/%m/%Y')
                if 2010 < d.year <= datetime.now().year:
                    lista_fechas.append(d)
            except: continue
        
        if lista_fechas:
            ultima_fecha = max(lista_fechas)
            ultima_fecha_str = ultima_fecha.strftime('%d/%m/%Y')
            hoy = datetime.now()
            meses_inactivo = (hoy.year - ultima_fecha.year) * 12 + (hoy.month - ultima_fecha.month)

    # Detección de Cesión y Notificación
    es_cesionario = "SÍ" if re.search(r'cesionario|contratado por', texto, re.I) else "NO"
    notificado = "SÍ" if any(x in texto.lower() for x in ["notificado", "notificación positiva"]) else "NO"
    
    # MATRIZ DE ESTADOS CRÍTICOS
    estado = "ACTIVO"
    if meses_inactivo >= 48: estado = "PRESCRIPCIÓN"
    elif meses_inactivo >= 6: estado = "CADUCIDAD"
    elif meses_inactivo >= 3 and notificado == "NO": estado = "NEGLIGENCIA"

    return {
        "Expediente": nombre_archivo,
        "Estado": estado,
        "Meses": meses_inactivo,
        "Ult_Gestion": ultima_fecha_str,
        "Cesion": es_cesionario,
        "Notif": notificado,
        "Timestamp": datetime.now().strftime('%d/%m/%Y %H:%M')
    }

st.title("🏛️ OBITER")
st.markdown("### Strategic Intelligence Framework")

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.header("📥 Data Ingestion")
    archivos = st.file_uploader("Upload PDF Corps", type="pdf", accept_multiple_files=True)
    if st.button("EXECUTE ANALYSIS"):
        if archivos:
            nuevos_registros = []
            for arc in archivos:
                lector = PyPDF2.PdfReader(arc)
                texto = "".join([p.extract_text() for p in lector.pages])
                nuevos_registros.append(extraer_dna_legal(texto, arc.name))
            
            # Actualizar memoria y guardar en CSV físico
            st.session_state['obiter_db'].extend(nuevos_registros)
            pd.DataFrame(st.session_state['obiter_db']).to_csv(DB_FILE, index=False)
            st.success(f"{len(archivos)} targets procesados.")

# --- CENTRAL DE INTELIGENCIA (EL DASHBOARD) ---
if st.session_state['obiter_db']:
    df = pd.DataFrame(st.session_state['obiter_db'])
    
    st.subheader("📊 Fleet Status")
    
    # Filtros de Eficiencia
    col1, col2 = st.columns(2)
    with col1:
        seleccion = st.multiselect(
            "Filter Anomalies:",
            ["PRESCRIPCIÓN", "CADUCIDAD", "NEGLIGENCIA", "ACTIVO"],
            default=["PRESCRIPCIÓN", "CADUCIDAD"]
        )
    
    df_filtrado = df[df['Estado'].isin(seleccion)] if seleccion else df

    # TABLA MAESTRA
    st.dataframe(df_filtrado, use_container_width=True)

    # MÉTRICAS ESTILO MUSK (KPIs de Negligencia)
    c1, c2, c3 = st.columns(3)
    c1.metric("CADUCIDAD", len(df[df['Estado'] == "CADUCIDAD"]))
    c2.metric("PRESCRIPCIÓN", len(df[df['Estado'] == "PRESCRIPCIÓN"]))
    c3.metric("NEGLIGENCIA", len(df[df['Estado'] == "NEGLIGENCIA"]))

    if st.button("RESET DATABASE (WIPE ALL)"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.session_state['obiter_db'] = []
        st.rerun()
else:
    st.info("System Idle. Waiting for data injection...")