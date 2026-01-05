import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
from datetime import datetime

# 1. Configuración de la página
st.set_page_config(page_title="Radar Legal - Modo Local", layout="wide", page_icon="⚖️")

st.title("⚖️ Radar Legal: Modo de Procesamiento Local")
st.info("Cargue el PDF una vez y explore los hallazgos en cada pestaña.")

# --- MOTOR DE BÚSQUEDA ---
def procesar_pdf(contenido_pdf, palabras_clave):
    try:
        with pdfplumber.open(BytesIO(contenido_pdf)) as pdf:
            resultados = []
            for i, pagina in enumerate(pdf.pages):
                texto = pagina.extract_text()
                if texto:
                    parrafos = texto.split('\n')
                    for parrafo in parrafos:
                        for palabra in palabras_clave:
                            if palabra.strip() and palabra.lower() in parrafo.lower():
                                resultados.append({
                                    "Página": i + 1,
                                    "Criterio": palabra,
                                    "DETALLE COMPLETO": parrafo.strip()
                                })
            return pd.DataFrame(resultados)
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return pd.DataFrame()

# --- BARRA LATERAL: CARGA ÚNICA ---
st.sidebar.header("📂 Entrada de Datos")
archivo_principal = st.sidebar.file_uploader("Suba el Boletín del día aquí:", type="pdf")

if archivo_principal:
    st.sidebar.success("✅ PDF cargado correctamente")
    datos_pdf = archivo_principal.getvalue()
else:
    st.sidebar.warning("⚠️ Por favor, suba un PDF para comenzar.")

# --- PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🏛️ Remates", "💰 Cobro Judicial/Embargos", "🚗 Lesiones Tránsito", "🔍 Rastrear Cliente"
])

# Lógica compartida para pestañas
def mostrar_resultados(lista_palabras, nombre_seccion):
    if archivo_principal:
        with st.spinner(f"Escaneando {nombre_seccion}..."):
            df = procesar_pdf(datos_pdf, lista_palabras)
            if not df.empty:
                st.success(f"Se encontraron {len(df)} registros en {nombre_seccion}")
                st.dataframe(df, use_container_width=True, height=400)
            else:
                st.warning(f"No se encontró información de {nombre_seccion} en este archivo.")
    else:
        st.error("Primero debe subir el PDF en la barra lateral izquierda.")

with tab1:
    st.subheader("Búsqueda de Remates Judiciales")
    if st.button("Ejecutar Análisis de Remates"):
        mostrar_resultados(["Remate", "Primer remate", "Finca", "Plano"], "Remates")

with tab2:
    st.subheader("Análisis de Cobro y Embargos")
    if st.button("Ejecutar Análisis de Cobro"):
        mostrar_resultados(["Cobro Judicial", "Embargo", "Decretado", "Mandamiento", "Monitorio"], "Cobro Judicial")

with tab3:
    st.subheader("Casos de Tránsito / Lesiones")
    if st.button("Ejecutar Análisis de Lesiones"):
        mostrar_resultados(["Lesiones culposas", "Tránsito", "Boleta", "Colisión"], "Lesiones")

with tab4:
    st.subheader("Búsqueda Específica de Cliente")
    cliente = st.text_input("Ingrese nombre o cédula del cliente:")
    if st.button("Buscar Cliente en el PDF"):
        if cliente:
            mostrar_resultados([cliente], f"Cliente: {cliente}")
        else:
            st.error("Debe ingresar un nombre o cédula.")
