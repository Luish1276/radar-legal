import streamlit as st
import pdfplumber
import re
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="OBITER - Sistema de Telemetría", layout="wide")

if 'obiter_db' not in st.session_state:
    st.session_state['obiter_db'] = []

def analizar_adn_expediente(file):
    texto_total = ""
    with pdfplumber.open(file) as pdf:
        for pagina in pdf.pages:
            texto_total += " " + (pagina.extract_text() or "")
    
    clean_text = " ".join(texto_total.lower().split())
    
    # 1. CESIÓN
    es_cesion = "SÍ" if any(x in clean_text for x in ["cesion", "cesionario", "contratado por", "cedente"]) else "NO"
    
    # 2. NOTIFICADO (Detección de Acta del Juzgado)
    patrones_notif = ["acta de notificacion", "diligenciada: si", "entregado al destinatario", "notificado"]
    esta_notif = "SÍ" if any(x in clean_text for x in patrones_notif) else "NO"
    
    # 3. ESTADO LEGAL (Telemetría de Tiempos)
    fechas = re.findall(r'\d{2}/\d{2}/\d{4}', texto_total)
    estado, meses, ult_fecha_str = "SIN DATOS", 0, "S/D"
    
    if fechas:
        lista_d = [datetime.strptime(f, '%d/%m/%Y') for f in fechas if 2010 < int(f[-4:]) <= 2026]
        if lista_d:
            ultima = max(lista_d)
            ult_fecha_str = ultima.strftime('%d/%m/%Y')
            
            # Fecha de referencia: 11 de enero de 2026
            hoy = datetime(2026, 1, 11)
            meses = (hoy.year - ultima.year) * 12 + (hoy.month - ultima.month)
            
            # Clasificación Técnica
            if meses >= 48: 
                estado = "PRESCRIPCIÓN"
            elif meses >= 6: 
                estado = "CADUCIDAD"
            else:
                estado = "ACTIVO (DENTRO DE TÉRMINO)"

    return {
        "Expediente": file.name,
        "Cesion": es_cesion,
        "Notificado": esta_notif,
        "Estado Final": estado,
        "Meses Inactividad": meses,
        "Última Gestión": ult_fecha_str
    }

st.title("🏛️ OBITER - Reporte de Estado")

archivos = st.file_uploader("Subir Expedientes", type="pdf", accept_multiple_files=True)

if st.button("EJECUTAR ANÁLISIS"):
    if archivos:
        for a in archivos:
            st.session_state['obiter_db'].append(analizar_adn_expediente(a))
        st.rerun()

if st.session_state['obiter_db']:
    df = pd.DataFrame(st.session_state['obiter_db'])
    st.markdown("### 📊 Fleet Status: Datos de Ejecución")
    st.dataframe(df, use_container_width=True)
    
    if st.button("LIMPIAR"):
        st.session_state['obiter_db'] = []
        st.rerun()