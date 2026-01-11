import streamlit as st
import pandas as pd
import PyPDF2
import re
from datetime import datetime

st.set_page_config(page_title="OBITER - Auditoría de Legitimación", layout="wide")

st.title("🏛️ OBITER: Análisis de Legitimidad y Embargos")
st.markdown("---")

def auditoria_profunda(texto):
    # --- 1. DETECCIÓN DE CESIÓN Y LEGITIMACIÓN ---
    # Buscamos el patrón que me diste: Contratado por XXX en condición de Cesionario
    patron_cesionario = re.search(r'contratado por\s+([A-Z\s\.]+)\s+en su condición de cesionario', texto, re.I)
    acreedor_original = re.search(r'suscrito originalmente por\s+([A-Z\s\.]+)', texto, re.I)
    
    # --- 2. DETECCIÓN DE BIENES (EMBARGOS) ---
    placas = re.search(r'vehículo placas\s+([A-Z0-9]+)', texto, re.I)
    captura = "SÍ" if "orden de captura" in texto.lower() else "NO"
    
    # --- 3. DATOS FINANCIEROS Y USURA ---
    monto = re.search(r'¢\s?([\d\.]+,\d{2})', texto)
    interes_mora = re.search(r'(\d+,\d+)%\s+mensual', texto)
    
    # --- 4. LÓGICA JURÍDICA ESTRATÉGICA ---
    hallazgos = []
    tipo_actor = "Acreedor Original"
    
    if patron_cesionario:
        tipo_actor = f"CESIONARIO ({patron_cesionario.group(1).strip()})"
        hallazgos.append(f"⚠️ **ALERTA DE LEGITIMACIÓN:** El actor es un cesionario. Verificar notificación al deudor (Art. 1101 C. Civil). Si no existe, cabe Incidente de Falta de Legitimidad.")
    
    if interes_mora:
        tasa = float(interes_mora.group(1).replace(',', '.'))
        if tasa > 2.5: # Umbral de usura aproximado
            hallazgos.append(f"🚩 **POSIBLE USURA:** Tasa moratoria del {tasa}% mensual excede los límites legales.")

    return {
        "actor": tipo_actor,
        "original": acreedor_original.group(1).strip() if acreedor_original else "No indicado",
        "monto": f"¢{monto.group(1)}" if monto else "No detectado",
        "placas": placas.group(1) if placas else "Ninguna",
        "orden_captura": captura,
        "hallazgos": hallazgos,
        "tasa": f"{interes_mora.group(1)}%" if interes_mora else "S/D"
    }

# --- INTERFAZ ---
archivo = st.file_uploader("Suba la Demanda o Certificación de Contador (PDF)", type="pdf")

if archivo:
    reader = PyPDF2.PdfReader(archivo)
    texto_total = "".join([p.extract_text() for p in reader.pages])
    res = auditoria_profunda(texto_total)

    # VISUALIZACIÓN PROFESIONAL
    st.subheader("🔍 Diagnóstico de Legitimación")
    c1, c2, c3 = st.columns(3)
    c1.metric("Actor Actual", res['actor'])
    c2.metric("Acreedor Original", res['original'])
    c3.metric("Monto Capital", res['monto'])

    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🚗 Activos y Embargos")
        st.write(f"**Vehículo Detectado:** {res['placas']}")
        st.write(f"**Solicitud de Captura:** {res['orden_captura']}")
        st.write(f"**Tasa Moratoria:** {res['tasa']}")

    with col_b:
        st.subheader("⚖️ Dictamen Estratégico")
        for h in res['hallazgos']:
            st.error(h) if "⚠️" in h or "🚩" in h else st.info(h)

    if not res['hallazgos']:
        st.success("No se detectaron anomalías evidentes en la legitimación.")