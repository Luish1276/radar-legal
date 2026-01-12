import streamlit as st
import pdfplumber
import re
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="OBITER - Diagnóstico de Falencias", layout="wide")

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
    
    # 2. NOTIFICADO (Lectura de Actas y Diligencias)
    patrones_notif = ["acta de notificacion", "diligenciada: si", "entregado al destinatario", "notificado"]
    esta_notif = "SÍ" if any(x in clean_text for x in patrones_notif) else "NO"
    
    # 3. ANÁLISIS DE TIEMPOS (Prescripción y Caducidad)
    fechas = re.findall(r'\d{2}/\d{2}/\d{4}', texto_total)
    prescripcion, caducidad, meses, ult_fecha, estado = "NO", "NO", 0, "S/D", "ACTIVO"
    
    if fechas:
        # Filtro de fechas (2010 a 2026)
        lista_d = [datetime.strptime(f, '%d/%m/%Y') for f in fechas if 2010 < int(f[-4:]) <= 2026]
        if lista_d:
            ultima = max(lista_d)
            ult_fecha = ultima.strftime('%d/%m/%Y')
            
            # Fecha de referencia para el cálculo: Enero 2026
            hoy = datetime(2026, 1, 11)
            meses = (hoy.year - ultima.year) * 12 + (hoy.month - ultima.month)
            
            # Evaluación Técnica de Plazos
            if meses >= 48: 
                prescripcion = "SÍ"
                estado = "PRESCRITO"
            if meses >= 6: 
                caducidad = "SÍ"
                if estado != "PRESCRITO": estado = "CADUCO"

    return {
        "Expediente": file.name,
        "Cesion": es_cesion,
        "Notificado": esta_notif,
        "Prescripción": prescripcion,
        "Caducidad": caducidad,
        "Meses Inactivo": meses,
        "Última Gestión": ult_fecha,
        "Estado": estado
    }

st.title("🏛️ OBITER - Fleet Status")

archivos = st.file_uploader("Inyectar Expedientes", type="pdf", accept_multiple_files=True)

if st.button("EJECUTAR DIAGNÓSTICO"):
    if archivos:
        for a in archivos:
            st.session_state['obiter_db'].append(analizar_adn_expediente(a))
        st.rerun()

if st.session_state['obiter_db']:
    df = pd.DataFrame(st.session_state['obiter_db'])
    
    # Reordenar columnas para que coincida exactamente con tu petición
    columnas_ordenadas = ["Expediente", "Cesion", "Notificado", "Prescripción", "Caducidad", "Meses Inactivo", "Última Gestión", "Estado"]
    df = df[columnas_ordenadas]
    
    st.markdown("### 📊 Diagnóstico de Falencias")
    st.dataframe(df, use_container_width=True)
    
    if st.button("LIMPIAR TABLA"):
        st.session_state['obiter_db'] = []
        st.rerun()