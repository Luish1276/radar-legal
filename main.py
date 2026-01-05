import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
from datetime import datetime
import re

# 1. Configuración
st.set_page_config(page_title="Radar Legal Analista", layout="wide")

st.title("⚖️ Radar Legal: Analista de Prescripciones y Cobros")

if 'pdf_data' not in st.session_state:
    st.session_state['pdf_data'] = None

# --- MOTOR ANALÍTICO ---
def analizar_texto_legal(texto, criterio):
    # 1. Extraer Expediente (Patrón común en CR)
    expediente = re.search(r'\d{2}-\d{6}-\d{4}-[A-Z]{2}', texto)
    exp_n = expediente.group(0) if expediente else "No detectado"
    
    # 2. Extraer Fechas
    fechas = re.findall(r'\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}', texto)
    prescripcion_msj = "Requiere revisión manual"
    probabilidad = "Baja"
    
    if fechas:
        try:
            # Asumimos que la primera fecha mencionada es la relevante
            fecha_doc = datetime.strptime(fechas[0].replace('-', '/'), '%d/%m/%Y')
            anios_transcurridos = (datetime.now() - fecha_doc).days / 365
            
            # Lógica de Prescripción (Simplificada)
            if "hipotecaria" in texto.lower() or "prendaria" in texto.lower():
                limite = 10
            else:
                limite = 4
                
            if anios_transcurridos >= limite:
                prescripcion_msj = f"⚠️ POSIBLE PRESCRIPCIÓN ({int(anios_transcurridos)} años)"
                probabilidad = "ALTA"
            else:
                prescripcion_msj = f"En plazo legal ({int(anios_transcurridos)} años)"
                probabilidad = "Baja"
        except:
            pass

    return {
        "Expediente": exp_n,
        "Tipo": "Ejecución / Cobro" if "ejecución" in texto.lower() else "Monitorio",
        "Hallazgo": criterio,
        "Análisis Prescripción": prescripcion_msj,
        "Probabilidad Éxito": probabilidad,
        "Texto Completo": texto[:500] + "..." # Para el Excel
    }

def procesar_pdf_analitico(contenido_pdf, palabras_clave, exclusiones=None):
    if exclusiones is None: exclusiones = []
    resultados = []
    
    with pdfplumber.open(BytesIO(contenido_pdf)) as pdf:
        for i, pagina in enumerate(pdf.pages):
            texto = pagina.extract_text()
            if texto:
                lineas = texto.split('\n')
                for idx, linea in enumerate(lineas):
                    for palabra in palabras_clave:
                        if palabra.lower() in linea.lower():
                            if any(exc.lower() in linea.lower() for exc in exclusiones):
                                continue
                            
                            # Tomamos el bloque para analizarlo
                            bloque = "\n".join(lineas[max(0, idx-2):idx+15])
                            analisis = analizar_texto_legal(bloque, palabra)
                            analisis["Página"] = i + 1
                            resultados.append(analisis)
    return pd.DataFrame(resultados)

# --- INTERFAZ ---
archivo = st.sidebar.file_uploader("Suba el PDF una vez:", type="pdf")
if archivo:
    st.session_state['pdf_data'] = archivo.getvalue()

tab1, tab2 = st.tabs(["📊 Resultados y Análisis", "📥 Exportar Datos"])

with tab1:
    if st.session_state['pdf_data']:
        palabras = ["Cobro Judicial", "Embargo", "Ejecución", "Monitorio", "Subasta", "Remate"]
        excl = ["Municipalidad", "Municipal"]
        
        if st.button("🚀 Iniciar Análisis Inteligente"):
            df_final = procesar_pdf_analitico(st.session_state['pdf_data'], palabras, excl)
            if not df_final.empty:
                st.session_state['df_resultados'] = df_final
                st.success("¡Análisis completado!")
                
                # Mostrar en pantalla de forma organizada
                st.dataframe(df_final[["Página", "Expediente", "Tipo", "Análisis Prescripción", "Probabilidad Éxito"]], use_container_width=True)
                
                for _, row in df_final.iterrows():
                    with st.expander(f"📁 Exp: {row['Expediente']} | {row['Análisis Prescripción']}"):
                        st.write(row['Texto Completo'])
            else:
                st.warning("No se encontraron casos relevantes.")
    else:
        st.info("Suba un PDF para comenzar.")

with tab2:
    if 'df_resultados' in st.session_state:
        st.subheader("Descargar Reporte para el Despacho")
        # Convertir a Excel (CSV para máxima compatibilidad)
        csv = st.session_state['df_resultados'].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Excel (CSV)",
            data=csv,
            file_name=f"reporte_radar_{datetime.now().strftime('%d_%m_%Y')}.csv",
            mime='text/csv',
        )
    else:
        st.write("Primero realice un análisis en la pestaña anterior.")
