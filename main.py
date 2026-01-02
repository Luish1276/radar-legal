import streamlit as st
import pdfplumber
import re
import requests
import io
from datetime import datetime, timedelta

# Configuración visual
st.set_page_config(page_title="Radar Legal CR", layout="wide")
st.title("⚖️ Radar Legal Avanzado - Costa Rica")

def buscar_boletin():
    cabeceras = {"User-Agent": "Mozilla/5.0"}
    for i in range(10):
        fecha = (datetime.now() - timedelta(days=i)).strftime("%d_%m_%Y")
        url = f"https://www.imprentanacional.go.cr/pub/boletin/{fecha}_BJ.pdf"
        try:
            r = requests.get(url, headers=cabeceras, timeout=10)
            if r.status_code == 200: return io.BytesIO(r.content), fecha
        except: continue
    return None, None

if st.button("🚀 INICIAR RASTREO TOTAL"):
    pdf_file, fecha_f = buscar_boletin()
    if pdf_file:
        st.success(f"Analizando Boletín del {fecha_f}")
        
        # Listas para clasificar hallazgos
        remates = []
        lesiones = []
        prescripciones = []

        with pdfplumber.open(pdf_file) as pdf:
            for pagina in pdf.pages[:50]: # Escaneamos más páginas para remates
                texto = pagina.extract_text()
                if texto:
                    lineas = texto.split('\n')
                    for linea in lineas:
                        # 1. BUSCAR REMATES (2019-2026)
                        if "REMATE" in linea.upper() or "FINCA" in linea.upper():
                            exp = re.search(r'(\d{2})-\d{6}-\d{4}-[A-Z]{2}', linea)
                            if exp:
                                año = int(exp.group(1))
                                if 19 <= año <= 26 or año == 0: # 0 por si es 2000
                                    remates.append({"Expediente": exp.group(), "Detalle": linea[:100]})

                        # 2. BUSCAR LESIONES CULPOSAS (Casos nuevos 25-26)
                        if "LESIONES CULPOSAS" in linea.upper():
                            exp = re.search(r'(\d{2})-\d{6}-\d{4}-[A-Z]{2}', linea)
                            if exp:
                                lesiones.append({"Expediente": exp.group(), "Texto": linea[:100]})

        # Mostrar resultados en pestañas profesionales
        tab1, tab2 = st.tabs(["🏠 Remates Inmuebles", "🚗 Lesiones Culposas"])
        
        with tab1:
            st.subheader("Posibles Remates Detectados (2019-2026)")
            st.table(remates) if remates else st.info("No hay remates hoy")
            
        with tab2:
            st.subheader("Casos de Lesiones Culposas Detectados")
            st.table(lesiones) if lesiones else st.info("No hay lesiones culposas hoy")
    else:
        st.error("No se pudo conectar con la Imprenta.")
