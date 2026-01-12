import streamlit as st
import pdfplumber
import re
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE IDENTIDAD (RADAR LEGAL)
st.set_page_config(page_title="RADAR LEGAL", layout="wide")

if 'radar_db' not in st.session_state:
    st.session_state['radar_db'] = []

def analizar_adn_expediente(file):
    texto_total = ""
    # Escaneo profundo de todas las páginas
    with pdfplumber.open(file) as pdf:
        for pagina in pdf.pages:
            texto_total += " " + (pagina.extract_text() or "")
    
    clean_text = " ".join(texto_total.lower().split())
    
    # --- COLUMNA 1: CESIÓN ---
    patrones_cesion = ["cesion", "cesionario", "contratado por", "cedente", "endoso"]
    es_cesion = "SÍ" if any(x in clean_text for x in patrones_cesion) else "NO"
    
    # --- COLUMNA 2: NOTIFICADO ---
    # Ajustado para detectar actas digitales y sellos de ventanilla
    patrones_notif = ["acta de notificacion", "diligenciada: si", "entregado al destinatario", "notificado", "notif.", "acuse"]
    esta_notif = "SÍ" if any(x in clean_text for x in patrones_notif) else "NO"
    
    # --- COLUMNAS 3, 4, 5 y 6: TIEMPOS Y ESTADO ---
    fechas = re.findall(r'\d{2}/\d{2}/\d{4}', texto_total)
    prescripcion, caducidad, meses, ult_fecha, estado = "NO", "NO", 0, "S/D", "ACTIVO"
    
    if fechas:
        # Filtro de seguridad para fechas coherentes
        lista_d = [datetime.strptime(f, '%d/%m/%Y') for f in fechas if 2010 < int(f[-4:]) <= 2026]
        if lista_d:
            ultima = max(lista_d)
            ult_fecha = ultima.strftime('%d/%m/%Y')
            
            # Cálculo de meses a la fecha actual (Enero 2026)
            hoy = datetime(2026, 1, 11)
            meses = (hoy.year - ultima.year) * 12 + (hoy.month - ultima.month)
            
            # Lógica de Diagnóstico
            if meses >= 48: 
                prescripcion = "SÍ"
                estado = "PRESCRITO"
            elif meses >= 6: 
                caducidad = "SÍ"
                estado = "CADUCO"
            else:
                estado = "ACTIVO"

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

# --- INTERFAZ DE USUARIO ---
st.title("🏛️ RADAR LEGAL")
st.markdown("### **Diagnóstico de Falencias de Flota**")

archivos = st.file_uploader("Inyectar Expedientes PDF", type="pdf", accept_multiple_files=True)

if st.button("EJECUTAR DIAGNÓSTICO"):
    if archivos:
        for a in archivos:
            resultado = analizar_adn_expediente(a)
            st.session_state['radar_db'].append(resultado)
        st.rerun()

if st.session_state['radar_db']:
    df = pd.DataFrame(st.session_state['radar_db'])
    
    # Orden exacto de las 8 columnas que solicitaste
    orden = ["Expediente", "Cesion", "Notificado", "Prescripción", "Caducidad", "Meses Inactivo", "Última Gestión", "Estado"]
    df = df[orden]
    
    st.markdown("---")
    st.markdown("#### 📊 Fleet Status")
    
    # Estilo para que el Estado se vea profesional
    def style_estado(v):
        color = 'red' if v in ['PRESCRITO', 'CADUCO'] else 'green'
        return f'color: {color}; font-weight: bold'
    
    st.dataframe(df.style.applymap(style_estado, subset=['Estado']), use_container_width=True)
    
    if st.button("LIMPIAR RADAR"):
        st.session_state['radar_db'] = []
        st.rerun()