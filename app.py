import streamlit as st
import pandas as pd
import PyPDF2
import re
from datetime import datetime

st.set_page_config(page_title="OBITER - Intelligence Unit", layout="wide")

st.title("🏛️ OBITER: Unidad de Auditoría Legal Estratégica")
st.markdown("---")

def dictamen_avanzado(texto):
    # --- 1. TRAZABILIDAD PROCESAL ---
    # Buscamos la última gestión del abogado
    fechas = re.findall(r'\d{2}/\d{2}/\d{4}', texto)
    hoy = datetime.now()
    dias_inactividad = 0
    ultima_fecha_str = "No detectada"
    if fechas:
        valid_dates = []
        for f in fechas:
            try:
                d = datetime.strptime(f, '%d/%m/%Y')
                if d.year > 2010 and d <= hoy: valid_dates.append(d)
            except: continue
        if valid_dates:
            ultima_fecha = max(valid_dates)
            ultima_fecha_str = ultima_fecha.strftime('%d/%m/%Y')
            dias_inactividad = (hoy - ultima_fecha).days

    # --- 2. LEGITIMACIÓN Y CESIÓN ---
    # ¿Quién es el dueño actual de la deuda?
    es_cesion = "SÍ" if any(x in texto.lower() for x in ["cesión", "cesionario", "contrato de venta de cartera"]) else "NO"
    
    # --- 3. AUDITORÍA DE NOTIFICACIÓN ---
    # El gran problema de las empresas de cobro: ¿Está notificado?
    if "notificación negativa" in texto.lower() or "no localizado" in texto.lower():
        estado_notificacion = "🔴 FALLIDA (Deudor inubicable)"
    elif "notificación positiva" in texto.lower() or "notificado personalmente" in texto.lower():
        estado_notificacion = "🟢 EXITOSA (Plazo de oposición corriendo)"
    else:
        estado_notificacion = "🟡 PENDIENTE / SIN RASTRO EN PDF"

    # --- 4. DETECCIÓN DE FALENCIAS TÉCNICAS ---
    falencias = []
    if dias_inactividad > 180: falencias.append("CADUCIDAD: Más de 6 meses de abandono procesal.")
    if es_cesion == "SÍ" and "notificación de cesión" not in texto.lower(): falencias.append("FALTA DE LEGITIMACIÓN: No consta notificación de la cesión al deudor.")
    if "prescripción" in texto.lower() and "interrumpe" not in texto.lower(): falencias.append("RIESGO DE PRESCRIPCIÓN: Mencionado en autos sin defensa activa.")

    return {
        "fecha_ult": ultima_fecha_str,
        "dias": dias_inactividad,
        "cesion": es_cesion,
        "notif": estado_notificacion,
        "falencias": falencias,
        "texto_completo": texto[:2000] # Para referencia
    }

# --- INTERFAZ PROFESIONAL ---
archivo_subido = st.file_uploader("Cargue el Expediente Judicial (PDF)", type="pdf")

if archivo_subido:
    reader = PyPDF2.PdfReader(archivo_subido)
    texto_total = "".join([p.extract_text() for p in reader.pages])
    res = dictamen_avanzado(texto_total)

    # PRESENTACIÓN DEL DICTAMEN (No una tabla vulgar)
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 Resumen de Auditoría")
        st.write(f"**Último movimiento detectado:** {res['fecha_ult']}")
        st.write(f"**Días de abandono procesal:** {res['dias']} días")
        st.write(f"**Estado de la Notificación:** {res['notif']}")
        st.write(f"**Cesión de Cartera:** {res['cesion']}")

    with col2:
        st.subheader("🚩 Hallazgos y Falencias")
        if res['falencias']:
            for f in res['falencias']:
                st.error(f)
        else:
            st.success("No se detectaron falencias críticas evidentes.")

    st.markdown("---")
    st.subheader("💡 Recomendación Estratégica")
    if res['dias'] > 180:
        st.warning("EL ABOGADO ABANDONÓ EL CASO. El expediente es vulnerable a una solicitud de Caducidad de Instancia por parte del deudor.")
    elif res['cesion'] == "SÍ":
        st.info("Revisar si la cesión cumple con el Art. 1101 del Código Civil. Podría atacarse la legitimidad del cobro si no hubo notificación previa.")