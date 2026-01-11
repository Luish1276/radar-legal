import streamlit as st
import pandas as pd
import PyPDF2
import re

st.set_page_config(page_title="Radar Legal", layout="wide")

def analizar_expediente(texto):
    # --- 1. DETECCIÓN AGRESIVA DE CESIONARIO ---
    # Si el texto menciona "cesionario" o que un contador fue contratado por alguien más
    es_cesionario = False
    actor_detectado = "Acreedor Original"
    
    # Buscamos el patrón que me diste
    if "cesionario" in texto.lower() or "contratado por" in texto.lower():
        es_cesionario = True
        # Intentamos extraer quién contrató al contador
        match_actor = re.search(r'contratado por\s+([A-Z\s\.]{3,50})', texto, re.I)
        if match_actor:
            actor_detectado = match_actor.group(1).strip()
        else:
            actor_detectado = "Cesionario No Identificado"

    # --- 2. EXTRACCIÓN DE DATOS DE LA DEMANDA ---
    monto = re.search(r'¢\s?([\d\.]+,\d{2})', texto)
    interes = re.search(r'(\d+,\d+)%\s+mensual', texto)
    placa = re.search(r'placas\s+([A-Z0-9]+)', texto, re.I)

    # --- 3. CONSTRUCCIÓN DEL DICTAMEN DE FALENCIAS ---
    falencias = []
    
    if es_cesionario:
        falencias.append("⚠️ FALTA DE LEGITIMACIÓN: El actor NO es el acreedor original. Es un Cesionario. Se debe verificar la notificación de cesión al deudor.")
    
    if "captura" in texto.lower():
        falencias.append("🚗 EMBARGO: Se solicita orden de captura de vehículo.")

    return {
        "Actor": actor_detectado,
        "Tipo": "CESIONARIO" if es_cesionario else "ACREEDOR ORIGINAL",
        "Monto Reclamado": f"¢{monto.group(1)}" if monto else "No detectado",
        "Tasa": f"{interes.group(1)}%" if interes else "No detectada",
        "Placa": placa.group(1) if placa else "No detectada",
        "Lista_Falencias": falencias
    }

# --- INTERFAZ SIMPLIFICADA (SIN TÍTULOS RAROS) ---
st.write("### Suba el Expediente para Análisis de Legitimación")
archivo = st.file_uploader("Archivo PDF", type="pdf")

if archivo:
    lector = PyPDF2.PdfReader(archivo)
    texto_completo = "".join([p.extract_text() for p in lector.pages])
    
    res = analizar_expediente(texto_completo)
    
    # MOSTRAR RESULTADOS DIRECTOS
    st.markdown("---")
    st.write(f"**IDENTIDAD DEL ACTOR:** {res['Actor']}")
    st.write(f"**CONDICIÓN:** {res['Tipo']}")
    st.write(f"**MONTO EN DEMANDA:** {res['Monto Reclamado']}")
    st.write(f"**VEHÍCULO A EMBARGAR:** {res['Placa']}")
    
    st.write("#### ⚖️ DICTAMEN DE FALENCIAS ENCONTRADAS:")
    if res['Lista_Falencias']:
        for f in res['Lista_Falencias']:
            st.error(f)
    else:
        st.success("No se detectaron falencias automáticas.")