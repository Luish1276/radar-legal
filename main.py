import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
from datetime import datetime
import re

# 1. Configuración de la plataforma
st.set_page_config(page_title="Radar Legal: Sistema Integral", layout="wide", page_icon="⚖️")

st.title("⚖️ Radar Legal: Defensa y Prescripción")
st.markdown("---")

if 'pdf_data' not in st.session_state:
    st.session_state['pdf_data'] = None

# --- MOTOR DE INTELIGENCIA LEGAL ---
def analizar_caso(texto, fuente="Gaceta"):
    # Extraer Expediente
    exp_match = re.search(r'\d{2}-\d{6}-\d{4}-[A-Z]{2}', texto)
    expediente = exp_match.group(0) if exp_match else "Desconocido"
    
    # Extraer Fechas (formato CR)
    fechas = re.findall(r'\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}', texto)
    analisis = "Sin fechas suficientes"
    alerta = "⚪"
    probabilidad = "N/A"

    if len(fechas) >= 1:
        try:
            # En Edictos, la primera fecha suele ser el auto que se intenta notificar
            fecha_auto = datetime.strptime(fechas[0].replace('-', '/'), '%d/%m/%Y')
            hoy = datetime.now()
            anios = (hoy - fecha_auto).days / 365
            
            # Determinamos plazo según tipo de deuda
            plazo_prescripcion = 10 if any(x in texto.lower() for x in ["hipotecaria", "prendaria"]) else 4
            
            if anios >= plazo_prescripcion:
                analisis = f"🔥 POSIBLE PRESCRIPCIÓN: {int(anios)} años desde el auto original."
                alerta = "🔴"
                probabilidad = "ALTA"
            elif anios >= (plazo_prescripcion - 1):
                analisis = f"⚠️ ALERTA: {int(anios)} años. Próximo a prescribir."
                alerta = "🟡"
                probabilidad = "MEDIA"
            else:
                analisis = f"✅ En plazo: {int(anios)} años transcurridos."
                alerta = "🟢"
                probabilidad = "BAJA"
        except:
            pass

    return {
        "Alerta": alerta,
        "Expediente": expediente,
        "Análisis": analisis,
        "Probabilidad": probabilidad,
        "Extracto": texto[:600] + "..."
    }

# --- PROCESADOR DE ARCHIVOS ---
def procesar_archivo(contenido, palabras_clave):
    resultados = []
    with pdfplumber.open(BytesIO(contenido)) as pdf:
        for i, pagina in enumerate(pdf.pages):
            texto = pagina.extract_text()
            if texto:
                lineas = texto.split('\n')
                for idx, linea in enumerate(lineas):
                    if any(p.lower() in linea.lower() for p in palabras_clave):
                        # Captura extendida para encontrar fechas y nombres
                        bloque = "\n".join(lineas[max(0, idx-3):idx+20])
                        data = analizar_caso(bloque)
                        data["Página"] = i + 1
                        resultados.append(data)
    return pd.DataFrame(resultados)

# --- INTERFAZ DE USUARIO ---
st.sidebar.header("📁 CARGA DE DOCUMENTOS")
tipo_doc = st.sidebar.radio("Tipo de documento:", ["Boletín Judicial (Gaceta)", "Historial de Gestión en Línea"])
archivo = st.sidebar.file_uploader("Subir PDF:", type="pdf")

if archivo:
    st.session_state['pdf_data'] = archivo.getvalue()
    st.sidebar.success("✅ Archivo cargado")

tab1, tab2, tab3 = st.tabs(["🔍 Escaneo de Oportunidades", "📊 Base de Datos Excel", "📖 Manual de Uso"])

with tab1:
    if st.session_state['pdf_data']:
        st.subheader(f"Analizando: {tipo_doc}")
        
        # Ajustamos búsqueda según tipo de documento
        if tipo_doc == "Boletín Judicial (Gaceta)":
            criterios = ["hace saber", "emplaza", "notifica", "notifíquese", "remate", "subasta"]
        else:
            criterios = ["demanda", "decreto", "embargo", "notificación"]

        if st.button("🚀 INICIAR RADAR"):
            df = procesar_archivo(st.session_state['pdf_data'], criterios)
            if not df.empty:
                st.session_state['resultados_radar'] = df
                # Mostrar semáforo de casos
                st.dataframe(df[["Alerta", "Expediente", "Análisis", "Probabilidad"]], use_container_width=True)
                
                for _, row in df.iterrows():
                    with st.expander(f"{row['Alerta']} EXP: {row['Expediente']} | {row['Probabilidad']}"):
                        st.text(row['Extracto'])
            else:
                st.warning("No se detectaron patrones de interés en este archivo.")
    else:
        st.info("👈 Cargue un archivo en la barra lateral para empezar.")

with tab2:
    if 'resultados_radar' in st.session_state:
        df_descarga = st.session_state['resultados_radar']
        st.subheader("Reporte de Hallazgos para el Despacho")
        st.write("Este archivo contiene los expedientes detectados y su análisis de prescripción.")
        
        csv = df_descarga.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar para Excel (.csv)",
            data=csv,
            file_name=f"radar_legal_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv'
        )
    else:
        st.write("No hay datos para exportar aún.")

with tab3:
    st.markdown("""
    ### Cómo usar tu Radar Legal:
    1. **Edictos (La Gaceta):** Sube el PDF de 'Notificaciones' o 'Remates'. El Radar buscará casos donde el auto es viejo pero la notificación es nueva. **¡Esas son tus defensas de prescripción!**
    2. **Gestión en Línea:** Sube el historial que descargas del Poder Judicial. El Radar buscará la fecha del último movimiento relevante.
    3. **Semáforo:** * 🔴 **Rojo:** Altísima probabilidad de ganar por prescripción.
       * 🟡 **Amarillo:** Caso en riesgo, revisar pronto.
       * 🟢 **Verde:** Caso activo y en plazo.
    """)
