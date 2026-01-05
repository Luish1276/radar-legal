import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
from datetime import datetime
import re
import os

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Radar Legal: Especialista en Defensa", layout="wide", page_icon="⚖️")

DB_FILE = "historial_defensas.csv"

def cargar_historial():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Fecha_Deteccion", "Alerta", "Expediente", "Tipo", "Análisis", "Probabilidad"])

def guardar_en_historial(df):
    hist_act = cargar_historial()
    df_f = pd.concat([hist_act, df]).drop_duplicates(subset=['Expediente'], keep='last')
    df_f.to_csv(DB_FILE, index=False)
    return len(df)

# --- MOTOR DE INTELIGENCIA CORREGIDO ---
def analizar_defensa_real(texto):
    # 1. Extraer Expediente
    exp_match = re.search(r'\d{2}-\d{6}-\d{4}-[A-Z]{2}', texto)
    expediente = exp_match.group(0) if exp_match else "S/N"
    
    # 2. Clasificación Crítica: ¿Es basura de remate o es oportunidad?
    palabras_remate = ["remate", "almoneda", "postores", "finca", "plano catastrado", "carrocería", "cilindrada"]
    es_remate = any(p in texto.lower() for p in palabras_remate)
    tipo = "🚨 REMATE (Ya ejecutado)" if es_remate else "🛡️ EMPLAZAMIENTO (Oportunidad)"
    
    # 3. Extracción de Fecha de Resolución (Evitando años de carros)
    # Buscamos años de resoluciones probables (entre 2010 y 2025) que NO estén cerca de "Modelo" o "Año"
    anio_actual = datetime.now().year
    anios_encontrados = re.findall(r'20\d{2}', texto)
    
    anio_resolucion = None
    for a in anios_encontrados:
        val = int(a)
        # Filtro: Si el texto cercano dice "año", "modelo" o "cilindrada", ignoramos ese 2018 o 2020
        if 2010 <= val <= anio_actual:
            # Una lógica simple: la fecha de la resolución suele ser la primera o la última mencionada lejos de datos técnicos
            anio_resolucion = val
            break

    # 4. Cálculo de Prescripción
    analisis, alerta, prob = "Sin fecha clara", "⚪", "N/A"
    if anio_resolucion:
        transcurrido = anio_actual - anio_resolucion
        # Limpiamos el error de los 1000 años
        if transcurrido > 30: transcurrido = 0 
        
        if transcurrido >= 4:
            analisis, alerta, prob = f"🔥 POSIBLE PRESCRIPCIÓN ({transcurrido} años)", "🔴", "ALTA"
        elif transcurrido == 3:
            analisis, alerta, prob = f"⚠️ RIESGO (3 años)", "🟡", "MEDIA"
        else:
            analisis, alerta, prob = f"En plazo ({transcurrido} años)", "🟢", "BAJA"

    return {
        "Fecha_Deteccion": datetime.now().strftime("%d/%m/%Y"),
        "Alerta": alerta,
        "Expediente": expediente,
        "Tipo": tipo,
        "Análisis": analisis,
        "Probabilidad": prob,
        "Texto": texto[:1000]
    }

# --- INTERFAZ ---
st.title("⚖️ Radar Legal: Filtro de Defensa Profesional")

if 'resultados' not in st.session_state: st.session_state['resultados'] = pd.DataFrame()

st.sidebar.header("📂 Entrada")
archivo = st.sidebar.file_uploader("Subir PDF:", type="pdf")

tab1, tab2 = st.tabs(["🔍 Escaneo Inteligente", "📚 Historial de Oportunidades"])

with tab1:
    col_a, col_b = st.columns([1, 2])
    with col_a:
        ocultar_remates = st.checkbox("🚫 Ocultar Remates (Ver solo Emplazamientos)", value=True)
    
    if archivo and st.button("🚀 Iniciar Análisis"):
        with pdfplumber.open(BytesIO(archivo.getvalue())) as pdf:
            hallazgos = []
            for pag in pdf.pages:
                txt = pag.extract_text()
                if txt:
                    # Buscamos los bloques por expediente
                    bloques = txt.split("EXP:") # La Gaceta suele separar así
                    for b in bloques:
                        if len(b) > 50:
                            res = analizar_defensa_real(b)
                            hallazgos.append(res)
            st.session_state['resultados'] = pd.DataFrame(hallazgos)

    df_viz = st.session_state['resultados']
    if not df_viz.empty:
        # Aplicar filtro de remates si el usuario quiere
        if ocultar_remates:
            df_viz = df_viz[df_viz['Tipo'].str.contains("EMPLAZAMIENTO")]

        st.dataframe(df_viz[["Alerta", "Expediente", "Tipo", "Análisis", "Probabilidad"]], use_container_width=True)
        
        if st.button("💾 Guardar Oportunidades en Historial"):
            op = df_viz[df_viz['Probabilidad'].isin(['ALTA', 'MEDIA'])]
            guardar_en_historial(op)
            st.success("Guardado en la biblioteca de casos.")

        for _, r in df_viz.iterrows():
            with st.expander(f"{r['Alerta']} {r['Expediente']} | {r['Tipo']}"):
                st.text(r['Texto'])

with tab2:
    h = cargar_historial()
    if not h.empty:
        st.table(h[["Fecha_Deteccion", "Alerta", "Expediente", "Análisis", "Probabilidad"]])
    else: st.write("Historial vacío.")
