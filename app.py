import streamlit as st
import PyPDF2
import re
from datetime import datetime
import pandas as pd

# 1. NOMBRE FIJO - IDENTIDAD DE MARCA
st.set_page_config(page_title="OBITER - Intelligence Unit", layout="wide")

# Inicializar la "Base de Datos" interna (Memoria de Sesión)
if 'database' not in st.session_state:
    st.session_state['database'] = []

def auditoria_core(texto, nombre_archivo):
    # Detección de fechas para inactividad
    fechas = re.findall(r'\d{2}/\d{2}/\d{4}', texto)
    meses_inactivo = 0
    ultima_fecha = "S/D"
    
    if fechas:
        lista_fechas = []
        for f in fechas:
            try:
                d = datetime.strptime(f, '%d/%m/%Y')
                if 2010 < d.year <= datetime.now().year:
                    lista_fechas.append(d)
            except: continue
        if lista_fechas:
            max_fecha = max(lista_fechas)
            ultima_fecha = max_fecha.strftime('%d/%m/%Y')
            meses_inactivo = (datetime.now().year - max_fecha.year) * 12 + (datetime.now().month - max_fecha.month)

    # Detección de Cesionario
    es_cesionario = "SÍ" if re.search(r'cesionario|contratado por', texto, re.I) else "NO"
    
    # Detección de Notificación
    notificado = "SÍ" if any(x in texto.lower() for x in ["notificado", "notificación positiva"]) else "NO"

    # Dictamen de Riesgo
    estado = "ACTIVO"
    if meses_inactivo >= 6: estado = "CADUCIDAD"
    elif meses_inactivo >= 3 and notificado == "NO": estado = "NEGLIGENCIA"

    # Estructura de datos para nuestra red interna
    registro = {
        "Fecha Análisis": datetime.now().strftime('%d/%m/%Y %H:%M'),
        "Expediente": nombre_archivo,
        "Última Gestión": ultima_fecha,
        "Meses Inactivo": meses_inactivo,
        "Cesion": es_cesionario,
        "Notificado": notificado,
        "Estado Crítico": estado
    }
    return registro

st.title("🏛️ OBITER")
st.markdown("### Radar de Negligencia y Central de Riesgo Procesal")

# --- SECCIÓN DE CARGA ---
with st.expander("📥 CARGAR NUEVOS EXPEDIENTES", expanded=True):
    archivos = st.file_uploader("Arrastre los PDFs aquí", type="pdf", accept_multiple_files=True)
    if st.button("PROCESAR Y GUARDAR EN RED"):
        if archivos:
            for arc in archivos:
                lector = PyPDF2.PdfReader(arc)
                texto = "".join([p.extract_text() for p in lector.pages])
                resultado = auditoria_core(texto, arc.name)
                # Guardar en nuestra base de datos interna
                st.session_state['database'].append(resultado)
            st.success(f"{len(archivos)} expedientes integrados a la red.")

# --- SECCIÓN DE BASE DE DATOS (EL "EQUIFAX" INTERNO) ---
st.markdown("---")
st.subheader("📊 Central de Inteligencia Acumulada")

if st.session_state['database']:
    df = pd.DataFrame(st.session_state['database'])
    
    # Filtros rápidos para toma de decisiones
    col1, col2 = st.columns(2)
    with col1:
        solo_caducidad = st.checkbox("Ver solo casos en CADUCIDAD")
    
    df_mostrar = df[df['Estado Crítico'] == "CADUCIDAD"] if solo_caducidad else df

    # Estilo Musk: Limpio y funcional
    st.dataframe(df_mostrar, use_container_width=True)

    # Botón para descargar toda la base de datos
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 EXPORTAR INTELIGENCIA (CSV)", csv, "obiter_db.csv", "text/csv")
else:
    st.info("La red está vacía. Inyecte datos subiendo expedientes.")