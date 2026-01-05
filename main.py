import streamlit as st
import pdfplumber
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime

# 1. Configuración de la página
st.set_page_config(page_title="Radar Legal - Cobros", layout="wide", page_icon="⚖️")

st.title("⚖️ Radar Legal: Especialista en Cobro Judicial")
st.markdown("---")

# --- MOTOR DE BÚSQUEDA MEJORADO ---
def buscar_en_archivo_detallado(contenido_pdf, palabras_clave):
    try:
        with pdfplumber.open(BytesIO(contenido_pdf)) as pdf:
            resultados = []
            for i, pagina in enumerate(pdf.pages):
                texto = pagina.extract_text()
                if texto:
                    # Dividimos el texto por párrafos (usualmente doble salto de línea o puntos y aparte)
                    parrafos = texto.split('\n') 
                    for p_num, parrafo in enumerate(parrafos):
                        for palabra in palabras_clave:
                            if palabra.strip() and palabra.lower() in parrafo.lower():
                                # Capturamos el párrafo completo donde está la palabra
                                resultados.append({
                                    "Página": i + 1,
                                    "Criterio": palabra,
                                    "NOTIFICACIÓN COMPLETA": parrafo.strip()
                                })
            return pd.DataFrame(resultados), None
    except Exception as e:
        return None, f"Error: {str(e)}"

# --- BARRA LATERAL ---
st.sidebar.header("📅 Consulta de Boletines")
fecha_consulta = st.sidebar.date_input("Fecha:", datetime.now())
dia, mes, anio = fecha_consulta.strftime("%d"), fecha_consulta.strftime("%m"), fecha_consulta.strftime("%Y")
url_boletin = f"https://www.imprentanacional.go.cr/boletin/?date={dia}/{mes}/{anio}"

# --- PESTAÑAS REDEFINIDAS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏛️ Remates", "💰 Cobro Judicial/Embargos", "🚗 Lesiones Tránsito", "🔍 Rastrear Cliente/Cédula", "📂 Analizar PDF Propio"
])

def ejecutar_busqueda_url(lista, titulo):
    with st.spinner(f"Analizando {titulo}..."):
        try:
            r = requests.get(url_boletin, timeout=15)
            if r.status_code != 200 or b'%PDF' not in r.content[:100]:
                st.info(f"No hay boletín disponible en el servidor para el {dia}/{mes}/{anio}.")
                return
            
            df, err = buscar_en_archivo_detallado(r.content, lista)
            if df is not None and not df.empty:
                st.success(f"¡Hallazgos encontrados en {titulo}!")
                # Ajustamos el diseño para que el texto largo se vea bien
                st.dataframe(df, use_container_width=True, height=500)
            else:
                st.warning(f"No se encontró información de {titulo}.")
        except:
            st.error("Error de conexión con la Imprenta.")

with tab1:
    if st.button("Buscar Remates"): 
        ejecutar_busqueda_url(["Remate", "Primer remate", "Finca"], "Remates")

with tab2:
    if st.button("Buscar Cobros y Embargos"):
        # Términos específicos de cobro judicial
        ejecutar_busqueda_url(["Cobro Judicial", "Embargo", "Decretado", "Mandamiento"], "Cobro Judicial")

with tab3:
    if st.button("Buscar Lesiones"): 
        ejecutar_busqueda_url(["Lesiones culposas", "Tránsito"], "Lesiones")

with tab4:
    cliente = st.text_input("Ingrese Cédula o Nombre Completo:")
    if st.button("Ejecutar Rastreo"):
        if cliente: ejecutar_busqueda_url([cliente], f"Cliente: {cliente}")

with tab5:
    st.subheader("📂 Analizador de PDFs Descargados")
    archivo = st.file_uploader("Suba el PDF de la sección que descargó (Remates, Avisos, etc.)", type="pdf")
    buscar_lo_siguiente = st.text_input("Palabra o cédula a buscar:")
    if archivo and st.button("Escanear Documento"):
        df_l, err_l = buscar_en_archivo_detallado(archivo.getvalue(), [buscar_lo_siguiente])
        if df_l is not None and not df_l.empty:
            st.success("Información encontrada:")
            st.table(df_l) # Usamos tabla para que el texto sea más legible aún
        else:
            st.warning("No se encontró el dato en este archivo.")
