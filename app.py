import streamlit as st
import PyPDF2
import re
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="OBITER - Intelligence Unit", layout="wide")

if 'obiter_db' not in st.session_state:
    st.session_state['obiter_db'] = []

def auditoria_ojo_de_aguila(texto, nombre):
    clean_text = " ".join(texto.lower().split())
    
    # 1. ANALISIS DE LEGITIMACIÓN (CESIÓN)
    es_cesion = "SÍ" if any(x in clean_text for x in ["cesion", "cesionario", "contratado por", "cedente", "endoso"]) else "NO"
    
    # 2. ANALISIS DE GESTIÓN (NOTIFICACIÓN)
    esta_notif = "SÍ" if any(x in clean_text for x in ["notificacion positiva", "notificado personalmente", "resultado positivo", "acta de notificacion"]) else "NO"
    
    # 3. ANALISIS DE TIEMPOS (EL CEREBRO DEL ROBOT)
    fechas = re.findall(r'\d{2}/\d{2}/\d{4}', texto)
    estado, meses = "ACTIVO", 0
    if fechas:
        lista_d = [datetime.strptime(f, '%d/%m/%Y') for f in fechas if 2010 < int(f[-4:]) <= 2026]
        if lista_d:
            ultima = max(lista_d)
            # Cálculo a hoy (Enero 2026)
            meses = (2026 - ultima.year) * 12 + (1 - ultima.month)
            
            # --- LÓGICA DE DECISIÓN LEGAL ---
            if meses >= 48: 
                estado = "💀 PRESCRIPCIÓN"
            elif meses >= 6: 
                estado = "🚩 CADUCIDAD"
            elif meses >= 3 and esta_notif == "NO":
                estado = "⚠️ NEGLIGENCIA (Notif. Pendiente)"

    return {
        "Expediente": nombre,
        "Cesion": es_cesion,
        "Notificado": esta_notif,
        "Estado Final": estado,
        "Meses Inactividad": meses,
        "Ultima Gestion": ultima.strftime('%d/%m/%Y') if fechas else "S/D"
    }

st.title("🏛️ OBITER")

archivos = st.file_uploader("Inyectar Expedientes", type="pdf", accept_multiple_files=True)

if st.button("EJECUTAR ANÁLISIS TÁCTICO"):
    if archivos:
        for a in archivos:
            lector = PyPDF2.PdfReader(a)
            t = "".join([p.extract_text() for p in lector.pages])
            st.session_state['obiter_db'].append(auditoria_ojo_de_aguila(t, a.name))
        st.rerun()

if st.session_state['obiter_db']:
    df = pd.DataFrame(st.session_state['obiter_db'])
    
    # Visualización de Alta Gerencia
    st.markdown("### 📊 Fleet Status: Diagnóstico de Falencias")
    
    # Resaltar filas críticas (Estilo Musk: que el error sea obvio)
    def highlight_status(val):
        color = 'red' if '💀' in val or '🚩' in val else 'orange' if '⚠️' in val else 'white'
        return f'background-color: {color}'

    st.dataframe(df, use_container_width=True)
    
    # KPI's Rápidos
    c1, c2, c3 = st.columns(3)
    c1.metric("CASOS PRESCRITOS", len(df[df['Estado Final'].str.contains("PRESCRIPCIÓN")]))
    c2.metric("CASOS CADUCOS", len(df[df['Estado Final'].str.contains("CADUCIDAD")]))
    c3.metric("CESIONES DETECTADAS", len(df[df['Cesion'] == "SÍ"]))

    if st.button("LIMPIAR CENTRAL"):
        st.session_state['obiter_db'] = []
        st.rerun()