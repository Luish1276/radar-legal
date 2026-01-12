import streamlit as st
import PyPDF2
import re
import pandas as pd
from datetime import datetime

# Identidad única
st.set_page_config(page_title="OBITER", layout="wide")

if 'obiter_db' not in st.session_state:
    st.session_state['obiter_db'] = []

def analizar_adn(texto, nombre):
    # Ojo de águila: lectura plana sin interferencias
    txt_clean = " ".join(texto.lower().split())
    
    # Variable 1: Cesión (Legitimación)
    es_cesion = "SÍ" if any(x in txt_clean for x in ["cesion", "cesionario", "contratado por", "cedente"]) else "NO"
    
    # Variable 2: Notificación (Gestión)
    esta_notif = "SÍ" if any(x in txt_clean for x in ["notificacion positiva", "notificado personalmente", "acta de notificacion", "resultado positivo"]) else "NO"
    
    # Variable 3: Estado (Tiempos de Abandono)
    fechas = re.findall(r'\d{2}/\d{2}/\d{4}', texto)
    estado, meses = "ACTIVO", 0
    if fechas:
        lista_d = [datetime.strptime(f, '%d/%m/%Y') for f in fechas if 2010 < int(f[-4:]) <= 2026]
        if lista_d:
            ultima = max(lista_d)
            # Cálculo exacto a hoy (Enero 2026)
            meses = (2026 - ultima.year) * 12 + (1 - ultima.month)
            if meses >= 48: estado = "PRESCRIPCIÓN"
            elif meses >= 6: estado = "CADUCIDAD"
            
    return {
        "Expediente": nombre,
        "Cesion": es_cesion,
        "Notificado": esta_notif,
        "Estado": estado,
        "Meses Inactivo": meses
    }

st.title("🏛️ OBITER")

# Interfaz de Ingesta
archivos = st.file_uploader("Inyectar Expedientes (PDF)", type="pdf", accept_multiple_files=True)

if st.button("EJECUTAR ANÁLISIS"):
    if archivos:
        for a in archivos:
            lector = PyPDF2.PdfReader(a)
            t = "".join([p.extract_text() for p in lector.pages])
            st.session_state['obiter_db'].append(analizar_adn(t, a.name))
        st.rerun()

# Central de Inteligencia
if st.session_state['obiter_db']:
    df = pd.DataFrame(st.session_state['obiter_db'])
    st.markdown("### 📊 Fleet Status")
    st.dataframe(df, use_container_width=True)
    
    if st.button("RESET"):
        st.session_state['obiter_db'] = []
        st.rerun()