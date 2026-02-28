import streamlit as st
import pdfplumber
import re
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURACIÓN DEL SISTEMA
st.set_page_config(page_title="RADAR LEGAL - Auditoría Integral", layout="wide")

if 'radar_db' not in st.session_state:
    st.session_state['radar_db'] = []

# --- MOTOR DE AUDITORÍA (REGLAS JURÍDICAS) ---
def analizar_pdf(file, nombre_archivo):
    texto_total = ""
    try:
        with pdfplumber.open(file) as pdf:
            for pagina in pdf.pages:
                texto_total += " " + (pagina.extract_text() or "")
    except Exception as e:
        return {"Error": f"No se pudo leer el PDF: {e}"}

    clean_text = " ".join(texto_total.lower().split())
    
    es_cesion = "SÍ" if any(x in clean_text for x in ["cesion", "cesionario", "cedente"]) else "NO"
    esta_notif = "SÍ" if any(x in clean_text for x in ["acta de notificacion", "notificado", "diligenciada: si"]) else "NO"
    
    fechas = re.findall(r'\d{2}/\d{2}/\d{4}', texto_total)
    meses, ult_fecha, estado, dictamen = 0, "S/D", "ACTIVO", "Gestión al día."
    es_prescrito = "NO"
    es_caduco = "NO"
    
    if fechas:
        lista_d = [datetime.strptime(f, '%d/%m/%Y') for f in fechas if 2010 < int(f[-4:]) <= 2026]
        if lista_d:
            ultima = max(lista_d)
            ult_fecha = ultima.strftime('%d/%m/%Y')
            hoy = datetime(2026, 1, 11)
            meses = (hoy.year - ultima.year) * 12 + (hoy.month - ultima.month)
            
            if meses >= 48: 
                es_prescrito = "SÍ (ALERTA)"
                estado = "PRESCRITO"
                dictamen = "🚨 CRÍTICO: Plazo de 4 años vencido."
            elif meses >= 6: 
                es_caduco = "SÍ (ABANDONO)"
                estado = "CADUCO"
                dictamen = f"⚠️ El abogado no ha gestionado en {meses} meses."

    return {
        "Dictamen Técnico": dictamen,
        "Expediente": nombre_archivo,
        "Estado": estado,
        "PRESCRIPCIÓN": es_prescrito,
        "CADUCIDAD": es_caduco,
        "Meses Inactivo": meses,
        "Última Gestión": ult_fecha,
        "Cesión": es_cesion,
        "Notificado": esta_notif
    }

# --- INTERFAZ ---
st.title("🏛️ RADAR LEGAL")
st.markdown(f"**Auditor Responsable:** Luis Humberto Varela Vargas | **Año:** 2026")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 Opción A: Subir Nuevo")
    archivos_subidos = st.file_uploader("Subir expedientes desde su PC", type="pdf", accept_multiple_files=True)
    if st.button("AUDITAR SUBIDOS"):
        if archivos_subidos:
            for a in archivos_subidos:
                st.session_state['radar_db'].append(analizar_pdf(a, a.name))
            st.rerun()

with col2:
    st.subheader("📂 Opción B: Desde el Sistema")
    archivos_locales = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    seleccionado = st.selectbox("Expedientes ya cargados:", archivos_locales if archivos_locales else ["No hay archivos"])
    if st.button("AUDITAR SELECCIONADO"):
        if seleccionado != "No hay archivos":
            with open(seleccionado, "rb") as f:
                st.session_state['radar_db'].append(analizar_pdf(f, seleccionado))
            st.rerun()

# --- REPORTE ---
if st.session_state['radar_db']:
    st.divider()
    st.header("📋 Reporte de Auditoría Jurídica")
    df = pd.DataFrame(st.session_state['radar_db'])
    orden = ["Dictamen Técnico", "Expediente", "Estado", "PRESCRIPCIÓN", "CADUCIDAD", "Meses Inactivo", "Última Gestión", "Cesión", "Notificado"]
    st.table(df[orden])
    
    if st.button("LIMPIAR TABLA"):
        st.session_state['radar_db'] = []
        st.rerun()