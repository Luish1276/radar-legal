import streamlit as st
import PyPDF2
import re
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="OBITER", layout="wide")

if 'obiter_db' not in st.session_state:
    st.session_state['obiter_db'] = []

def auditoria_profunda(pdf_reader, nombre_archivo):
    texto_completo = ""
    # Escaneamos TODAS las páginas para no perder resoluciones al final del archivo
    for pagina in pdf_reader.pages:
        texto_completo += " " + (pagina.extract_text() or "")
    
    clean_text = " ".join(texto_completo.lower().split())
    
    # 1. CESIÓN (Legitimación)
    patrones_cesion = ["cesion", "cesionario", "contratado por", "cedente", "endoso", "sustitucion procesal"]
    es_cesion = "SÍ" if any(x in clean_text for x in patrones_cesion) else "NO"
    
    # 2. NOTIFICACIÓN (Ojo de Águila Reforzado)
    # Buscamos no solo la palabra, sino la acción judicial de notificar
    patrones_notif = [
        "notificacion positiva", "notificado personalmente", "acta de notificacion", 
        "cedula de notificacion", "notificacion exitosa", "resultado positivo",
        "concedase la notificacion", "notificacion por boletin", "constancia de notificacion"
    ]
    esta_notif = "SÍ" if any(x in clean_text for x in patrones_notif) else "NO"
    
    # 3. ÚLTIMA GESTIÓN (Escritos y Resoluciones)
    # Buscamos todas las fechas para encontrar el último movimiento real del abogado
    fechas = re.findall(r'\d{2}/\d{2}/\d{4}', texto_completo)
    estado, meses, ult_fecha_str = "ACTIVO", 0, "S/D"
    
    if fechas:
        lista_d = [datetime.strptime(f, '%d/%m/%Y') for f in fechas if 2010 < int(f[-4:]) <= 2026]
        if lista_d:
            ultima = max(lista_d)
            ult_fecha_str = ultima.strftime('%d/%m/%Y')
            # Cálculo a Enero 2026
            meses = (2026 - ultima.year) * 12 + (1 - ultima.month)
            
            if meses >= 48: estado = "PRESCRIPCIÓN"
            elif meses >= 6: estado = "CADUCIDAD"

    return {
        "Expediente": nombre_archivo,
        "Cesion": es_cesion,
        "Notificado": esta_notif,
        "Estado Final": estado,
        "Meses Inactividad": meses,
        "Ultima Gestion": ult_fecha_str
    }

st.title("🏛️ OBITER")

archivos = st.file_uploader("Inyectar Expedientes", type="pdf", accept_multiple_files=True)

if st.button("EJECUTAR ANÁLISIS"):
    if archivos:
        for a in archivos:
            lector = PyPDF2.PdfReader(a)
            resultado = auditoria_profunda(lector, a.name)
            st.session_state['obiter_db'].append(resultado)
        st.rerun()

if st.session_state['obiter_db']:
    df = pd.DataFrame(st.session_state['obiter_db'])
    st.markdown("### 📊 Fleet Status: Diagnóstico de Falencias")
    st.dataframe(df, use_container_width=True)
    
    if st.button("LIMPIAR CENTRAL"):
        st.session_state['obiter_db'] = []
        st.rerun()