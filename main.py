import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
from datetime import datetime
import re
import os

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Radar Legal: Inteligencia de Defensa", layout="wide", page_icon="⚖️")

# Archivo de Base de Datos Local
DB_FILE = "historial_casos.csv"

# --- FUNCIONES DE BASE DE DATOS ---
def cargar_historial():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Fecha_Deteccion", "Alerta", "Expediente", "Análisis", "Probabilidad", "Fuente"])

def guardar_en_historial(df_nuevos):
    historial_actual = cargar_historial()
    df_final = pd.concat([historial_actual, df_nuevos]).drop_duplicates(subset=['Expediente'], keep='last')
    df_final.to_csv(DB_FILE, index=False)
    return len(df_nuevos)

# --- MOTOR DE INTELIGENCIA LEGAL ---
def analizar_caso_detallado(texto):
    # Extraer Expediente
    exp_match = re.search(r'\d{2}-\d{6}-\d{4}-[A-Z]{2}', texto)
    expediente = exp_match.group(0) if exp_match else f"S/N-{datetime.now().microsecond}"
    
    # Extraer Fechas
    fechas = re.findall(r'\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}', texto)
    analisis, alerta, prob = "Sin fechas detectadas", "⚪", "N/A"

    if fechas:
        try:
            fecha_auto = datetime.strptime(fechas[0].replace('-', '/'), '%d/%m/%Y')
            anios = (datetime.now() - fecha_auto).days / 365
            
            # Lógica de plazos: Hipotecario/Prendario 10 años, otros 4 años
            plazo = 10 if any(x in texto.lower() for x in ["hipotecaria", "prendaria"]) else 4
            
            if anios >= plazo:
                analisis, alerta, prob = f"🔥 POSIBLE PRESCRIPCIÓN ({int(anios)} años)", "🔴", "ALTA"
            elif anios >= (plazo - 1):
                analisis, alerta, prob = f"⚠️ RIESGO PRÓXIMO ({int(anios)} años)", "🟡", "MEDIA"
            else:
                analisis, alerta, prob = f"En plazo legal ({int(anios)} años)", "🟢", "BAJA"
        except: pass

    return {
        "Fecha_Deteccion": datetime.now().strftime("%d/%m/%Y"),
        "Alerta": alerta,
        "Expediente": expediente,
        "Análisis": analisis,
        "Probabilidad": prob,
        "Texto": texto[:1000] # Guardamos el bloque para lectura
    }

# --- PROCESAMIENTO DE PDF ---
def procesar_boletin(contenido_pdf, criterios, exclusiones):
    resultados = []
    with pdfplumber.open(BytesIO(contenido_pdf)) as pdf:
        for i, pagina in enumerate(pdf.pages):
            texto_pag = pagina.extract_text()
            if texto_pag:
                lineas = texto_pag.split('\n')
                for idx, linea in enumerate(lineas):
                    if any(c.lower() in linea.lower() for c in criterios):
                        # Evitar municipalidades si se solicita
                        if any(exc.lower() in linea.lower() for exc in exclusiones):
                            continue
                        
                        # Capturar bloque de contexto (18 líneas)
                        bloque = "\n".join(lineas[max(0, idx-2):idx+16])
                        data = analizar_caso_detallado(bloque)
                        data["Página"] = i + 1
                        resultados.append(data)
    return pd.DataFrame(resultados)

# --- INTERFAZ DE USUARIO ---
st.title("⚖️ Radar Legal Pro")
st.markdown("---")

if 'resultados_radar' not in st.session_state:
    st.session_state['resultados_radar'] = pd.DataFrame()

# Barra Lateral Independiente
st.sidebar.header("📂 Carga de Documentos")
archivo = st.sidebar.file_uploader("Subir PDF del Boletín Judicial:", type="pdf")
if archivo:
    st.sidebar.success("✅ Documento cargado")

# Pestañas de Trabajo
tab1, tab2, tab3 = st.tabs(["🔍 Análisis de Oportunidades", "📚 Historial de Prescripciones", "⚙️ Configuración"])

with tab1:
    st.subheader("Buscador de Edictos y Notificaciones")
    if archivo:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Iniciar Escaneo de Prescripciones"):
                # Criterios específicos para encontrar deudores no notificados o remates viejos
                criterios_busqueda = ["hace saber", "emplaza", "notifica", "remate", "subasta", "continuar sin oferentes"]
                excluir_temas = ["municipalidad", "municipal", "patentes"]
                
                df = procesar_boletin(archivo.getvalue(), criterios_busqueda, excluir_temas)
                st.session_state['resultados_radar'] = df
        
        if not st.session_state['resultados_radar'].empty:
            df_res = st.session_state['resultados_radar']
            st.dataframe(df_res[["Alerta", "Expediente", "Análisis", "Probabilidad", "Página"]], use_container_width=True)
            
            if st.button("💾 Guardar casos rojos y amarillos en Historial"):
                # Solo guardamos los que tienen potencial
                para_guardar = df_res[df_res['Probabilidad'].isin(['ALTA', 'MEDIA'])]
                count = guardar_en_historial(para_guardar)
                st.success(f"Se han archivado {count} expedientes con potencial de defensa.")
                st.balloons()
            
            for _, row in df_res.iterrows():
                with st.expander(f"{row['Alerta']} EXP: {row['Expediente']} | {row['Análisis']}"):
                    st.text(row['Texto'])
    else:
        st.info("Suba un archivo PDF en el panel de la izquierda para comenzar el rastreo.")

with tab2:
    st.subheader("📚 Biblioteca de Expedientes Ganables")
    historial = cargar_historial()
    
    if not historial.empty:
        st.write("Estos son los casos que has detectado en días anteriores:")
        st.table(historial[["Fecha_Deteccion", "Alerta", "Expediente", "Análisis", "Probabilidad"]])
        
        csv = historial.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Base de Datos (CSV)", data=csv, file_name="historial_radar_legal.csv", mime="text/csv")
    else:
        st.write("Tu archivo histórico está vacío. Guarda hallazgos desde la pestaña de Escaneo.")

with tab3:
    st.subheader("⚙️ Configuración del Radar")
    st.text_input("Nombre del Despacho:", "Radar Legal")
    st.write("Versión del Sistema: 2.0 (Filtros de Prescripción Activados)")
