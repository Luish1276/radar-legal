import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
from datetime import datetime
import re
import os

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Radar Legal: Analista Pro", layout="wide", page_icon="⚖️")

DB_FILE = "historial_defensas.csv"

def cargar_historial():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Fecha_Deteccion", "Alerta", "Expediente", "Tipo", "Análisis", "Probabilidad"])

def guardar_en_historial(df):
    hist_act = cargar_historial()
    df_f = pd.concat([hist_act, df]).drop_duplicates(subset=['Expediente'], keep='last')
    df_f.to_csv(DB_FILE, index=False)
    return len(df)

# --- MOTOR DE INTELIGENCIA ---
def analizar_bloque(texto, es_expediente_completo=False):
    exp_match = re.search(r'\d{2}-\d{6}-\d{4}-[A-Z]{2}', texto)
    expediente = exp_match.group(0) if exp_match else "S/N"
    
    # Si es un expediente judicial completo, buscamos la fecha más reciente de gestión útil
    # Si es de La Gaceta, buscamos la fecha del auto
    anio_actual = datetime.now().year
    anios_encontrados = re.findall(r'20\d{2}', texto)
    
    anio_referencia = None
    if anios_encontrados:
        # En expedientes judiciales, nos interesa la fecha de la última resolución
        # En La Gaceta, la fecha del auto de emplazamiento
        validos = [int(a) for a in anios_encontrados if 2010 <= int(a) <= anio_actual]
        if validos:
            anio_referencia = min(validos) if not es_expediente_completo else max(validos)

    analisis, alerta, prob = "Sin fecha clara", "⚪", "N/A"
    if anio_referencia:
        transcurrido = anio_actual - anio_referencia
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
        "Análisis": analisis,
        "Probabilidad": prob,
        "Texto": texto[:1000]
    }

# --- INTERFAZ ---
st.title("⚖️ Radar Legal: Especialista en Defensa")

tab1, tab2 = st.tabs(["🔍 Escaneo de La Gaceta", "🔬 Analizar Expediente Judicial (PDF de Gestión)"])

with tab1:
    st.header("Buscador de Oportunidades en Edictos")
    archivo_gaceta = st.file_uploader("Suba el PDF de La Gaceta:", type="pdf", key="gaceta")
    
    if archivo_gaceta and st.button("🚀 Escanear La Gaceta"):
        with pdfplumber.open(BytesIO(archivo_gaceta.getvalue())) as pdf:
            hallazgos = []
            for pag in pdf.pages:
                txt = pag.extract_text()
                if txt:
                    bloques = txt.split("EXP:")
                    for b in bloques:
                        if len(b) > 50:
                            # Filtro anti-remates automático aquí
                            if not any(p in b.lower() for p in ["remate", "carrocería", "finca"]):
                                hallazgos.append(analizar_bloque(b))
            
            df_g = pd.DataFrame(hallazgos)
            if not df_g.empty:
                st.dataframe(df_g[["Alerta", "Expediente", "Análisis", "Probabilidad"]], use_container_width=True)
                if st.button("💾 Guardar en mi Base de Datos"):
                    guardar_en_historial(df_g[df_g['Probabilidad'].isin(['ALTA', 'MEDIA'])])
                    st.success("Guardado.")

with tab2:
    st.header("Análisis de Expediente del Poder Judicial")
    st.info("Suba aquí el PDF que descarga de 'Gestión en Línea' para calcular la prescripción de ese caso específico.")
    
    archivo_pj = st.file_uploader("Suba el PDF del Expediente Judicial:", type="pdf", key="pj")
    
    if archivo_pj and st.button("🔬 Analizar Movimientos"):
        with pdfplumber.open(BytesIO(archivo_pj.getvalue())) as pdf:
            todo_el_texto = ""
            for pag in pdf.pages:
                todo_el_texto += pag.extract_text() + "\n"
            
            # Analizamos el expediente como un todo
            resultado = analizar_bloque(todo_el_texto, es_expediente_completo=True)
            
            st.subheader("Resultado del Análisis Forense:")
            col1, col2, col3 = st.columns(3)
            col1.metric("Expediente", resultado["Expediente"])
            col2.metric("Estado de Prescripción", resultado["Análisis"])
            col3.metric("Probabilidad de Éxito", resultado["Probabilidad"])
            
            with st.expander("Ver detalles del análisis"):
                st.write("El sistema ha detectado las fechas de los movimientos y ha calculado el tiempo de inactividad o el plazo desde el auto principal.")
                st.text(todo_el_texto[:1500] + "...")

    st.markdown("---")
    st.subheader("📚 Tus Casos Guardados")
    h = cargar_historial()
    if not h.empty:
        st.dataframe(h[["Fecha_Deteccion", "Alerta", "Expediente", "Análisis", "Probabilidad"]], use_container_width=True)
    else:
        st.write("No hay casos en el historial aún.")
