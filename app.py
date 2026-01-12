import streamlit as st
import pdfplumber
import re
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="OBITER - High Precision", layout="wide")

if 'obiter_db' not in st.session_state:
    st.session_state['obiter_db'] = []

def analizar_adn_expediente(file):
    texto_total = ""
    # ESCANEO TOTAL: No dejamos ni una página por fuera
    with pdfplumber.open(file) as pdf:
        for pagina in pdf.pages:
            texto_total += " " + (pagina.extract_text() or "")
    
    clean_text = " ".join(texto_total.lower().split())
    
    # 1. COLUMNA CESIÓN
    # Buscamos la cesión de Promerica que aparece en tu documento
    patrones_cesion = ["cesion", "cesionario", "contratado por", "cedente", "endoso"]
    es_cesion = "SÍ" if any(x in clean_text for x in patrones_cesion) else "NO"
    
    # 2. COLUMNA NOTIFICADO (Precisión Quirúrgica)
    # Tu expediente usa "Diligenciada: SI" y "Acta de Notificación"
    patrones_notif = [
        "acta de notificacion", "diligenciada: si", "entregado al destinatario",
        "notificacion positiva", "cedula", "notificado personalmente"
    ]
    esta_notif = "SÍ" if any(x in clean_text for x in patrones_notif) else "NO"
    
    # 3. COLUMNAS ESTADO Y MESES (Regla de Oro: 6 y 48)
    fechas = re.findall(r'\d{2}/\d{2}/\d{4}', texto_total)
    estado, meses, ult_fecha_str = "ACTIVO", 0, "S/D"
    
    if fechas:
        # Filtramos para ignorar fechas basura y quedarnos con movimientos judiciales
        lista_d = [datetime.strptime(f, '%d/%m/%Y') for f in fechas if 2010 < int(f[-4:]) <= 2026]
        if lista_d:
            ultima = max(lista_d)
            ult_fecha_str = ultima.strftime('%d/%m/%Y')
            # Cálculo a Enero 2026
            hoy = datetime(2026, 1, 11)
            meses = (hoy.year - ultima.year) * 12 + (hoy.month - ultima.month)
            
            if meses >= 48: estado = "PRESCRIPCIÓN"
            elif meses >= 6: estado = "CADUCIDAD"

    return {
        "Expediente": file.name,
        "Cesion": es_cesion,
        "Notificado": esta_notif,
        "Estado Final": estado,
        "Meses Inactivo": meses,
        "Ultima Gestion": ult_fecha_str
    }

# INTERFAZ OBITER
st.title("🏛️ OBITER - Fleet Status")

archivos = st.file_uploader("Inyectar Expedientes PDF", type="pdf", accept_multiple_files=True)

if st.button("EJECUTAR ANÁLISIS CRÍTICO"):
    if archivos:
        for a in archivos:
            resultado = analizar_adn_expediente(a)
            st.session_state['obiter_db'].append(resultado)
        st.rerun()

if st.session_state['obiter_db']:
    df = pd.DataFrame(st.session_state['obiter_db'])
    st.markdown("### 📊 Resultados del Diagnóstico")
    st.dataframe(df, use_container_width=True)
    
    if st.button("LIMPIAR TABLA"):
        st.session_state['obiter_db'] = []
        st.rerun()