import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO

# 1. Configuración de la página
st.set_page_config(page_title="Radar Legal - Cobros", layout="wide", page_icon="⚖️")

st.title("⚖️ Radar Legal: Especialista en Cobro Judicial")
st.info("Cargue el PDF y el sistema extraerá la información completa del edicto.")

# --- MOTOR DE BÚSQUEDA ROBUSTO ---
def procesar_pdf_detallado(contenido_pdf, palabras_clave):
    try:
        with pdfplumber.open(BytesIO(contenido_pdf)) as pdf:
            resultados = []
            for i, pagina in enumerate(pdf.pages):
                texto = pagina.extract_text()
                if texto:
                    lineas = texto.split('\n')
                    for index, linea in enumerate(lineas):
                        for palabra in palabras_clave:
                            if palabra.strip() and palabra.lower() in linea.lower():
                                # CAPTURA DE CONTEXTO: Tomamos la línea donde está la palabra 
                                # + las 15 líneas siguientes para no perder el detalle del remate
                                inicio = index
                                fin = min(len(lineas), index + 16)
                                bloque_completo = "\n".join(lineas[inicio:fin])
                                
                                resultados.append({
                                    "Página": i + 1,
                                    "Criterio": palabra,
                                    "EDICTO / NOTIFICACIÓN COMPLETA": bloque_completo
                                })
            return pd.DataFrame(resultados)
    except Exception as e:
        st.error(f"Error técnico: {e}")
        return pd.DataFrame()

# --- BARRA LATERAL ---
st.sidebar.header("📂 Entrada de Datos")
archivo_principal = st.sidebar.file_uploader("Suba el PDF aquí:", type="pdf")

if archivo_principal:
    datos_pdf = archivo_principal.getvalue()
    st.sidebar.success("✅ Archivo listo")
else:
    st.sidebar.warning("⚠️ Suba un PDF para comenzar.")

# --- PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🏛️ Remates", "💰 Cobro Judicial/Embargos", "🚗 Lesiones Tránsito", "🔍 Rastrear Cliente"
])

def mostrar_hallazgos(lista, seccion):
    if archivo_principal:
        df = procesar_pdf_detallado(datos_pdf, lista)
        if not df.empty:
            st.success(f"Hallazgos en {seccion}:")
            # Usamos st.table para que el texto largo no se corte y sea fácil de leer
            for idx, row in df.iterrows():
                with st.expander(f"📍 Página {row['Página']} - Coincidencia: {row['Criterio']}"):
                    st.text(row['EDICTO / NOTIFICACIÓN COMPLETA'])
                    st.markdown("---")
        else:
            st.warning(f"No se encontró nada relacionado a {seccion}.")
    else:
        st.error("Suba el archivo en la izquierda.")

with tab1:
    if st.button("Analizar Remates"):
        mostrar_hallazgos(["Remate", "Primer remate", "continuar sin oferentes", "señalan las"], "Remates")

with tab2:
    if st.button("Analizar Cobros"):
        mostrar_hallazgos(["Cobro Judicial", "Embargo", "Decretado", "Mandamiento"], "Cobros")

with tab3:
    if st.button("Analizar Tránsito"):
        mostrar_hallazgos(["Lesiones culposas", "Tránsito"], "Tránsito")

with tab4:
    cliente = st.text_input("Nombre o Cédula:")
    if st.button("Buscar en PDF"):
        if cliente: mostrar_hallazgos([cliente], f"Cliente: {cliente}")
