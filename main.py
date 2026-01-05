import streamlit as st
import pdfplumber
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime

# ESTA DEBE SER LA LÍNEA 8 (O LA PRIMERA LÍNEA DE CÓDIGO DESPUÉS DE LOS IMPORTS)
st.set_page_config(page_title="Radar Legal CR", layout="wide", page_icon="⚖️")

st.title("⚖️ Radar Legal Avanzado - Costa Rica")
st.markdown("---")

# --- MOTOR DE BÚSQUEDA ---
def buscar_en_archivo(contenido_pdf, palabras_clave):
    try:
        with pdfplumber.open(BytesIO(contenido_pdf)) as pdf:
            resultados = []
            for i, pagina in enumerate(pdf.pages):
                texto = pagina.extract_text()
                if texto:
                    for palabra in palabras_clave:
                        if palabra.strip() and palabra.lower() in texto.lower():
                            inicio = max(0, texto.lower().find(palabra.lower()) - 100)
                            fin = inicio + 250
                            contexto = "..." + texto[inicio:fin] + "..."
                            resultados.append({
                                "Página": i + 1,
                                "Palabra": palabra,
                                "Extracto": contexto.replace("\n", " ")
                            })
            return pd.DataFrame(resultados), None
    except Exception as e:
        return None, f"Error al leer el PDF: {str(e)}"

# --- BARRA LATERAL ---
st.sidebar.header("📅 Boletín de la Imprenta")
fecha_consulta = st.sidebar.date_input("Seleccione fecha:", datetime.now())
dia, mes, anio = fecha_consulta.strftime("%d"), fecha_consulta.strftime("%m"), fecha_consulta.strftime("%Y")
url_boletin = f"https://www.imprentanacional.go.cr/boletin/?date={dia}/{mes}/{anio}"

# --- PESTAÑAS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏛️ Remates", "🚗 Lesiones", "⚖️ Prescripciones", "🔍 Consulta Cliente", "📂 Analizar PDF Propio"
])

def ejecutar_busqueda_url(lista):
    with st.spinner("Buscando en la Imprenta..."):
        try:
            r = requests.get(url_boletin, timeout=15)
            if r.status_code != 200 or b'%PDF' not in r.content[:100]:
                st.info("No hay boletín para esta fecha.")
                return
            df, err = buscar_en_archivo(r.content, lista)
            if df is not None and not df.empty:
                st.success("¡Hallazgos encontrados!")
                st.dataframe(df, use_container_width=True)
            else: st.warning("Sin resultados.")
        except: st.error("Error de conexión.")

with tab1:
    if st.button("Buscar Remates"): ejecutar_busqueda_url(["Remate", "Primer remate"])
with tab2:
    if st.button("Buscar Lesiones"): ejecutar_busqueda_url(["Lesiones culposas", "Tránsito"])
with tab3:
    if st.button("Buscar Prescripciones"): ejecutar_busqueda_url(["Prescripción"])
with tab4:
    cliente = st.text_input("Nombre o Cédula:")
    if st.button("Rastrear"): ejecutar_busqueda_url([cliente])

with tab5:
    st.subheader("📂 Analizador de Archivos PDF")
    archivo_subido = st.file_uploader("Subir PDF (Gacetas viejas, edictos, etc.)", type="pdf")
    palabras_a_buscar = st.text_input("¿Qué palabras buscamos?", "Remate, Cédula")
    
    if archivo_subido is not None:
        if st.button("🚀 Iniciar Escaneo de Archivo"):
            with st.spinner("Analizando..."):
                bytes_data = archivo_subido.getvalue() 
                lista_keywords = [p.strip() for p in palabras_a_buscar.split(",")]
                df_local, error_local = buscar_en_archivo(bytes_data, lista_keywords)
                if df_local is not None and not df_local.empty:
                    st.success(f"Encontrado en el archivo.")
                    st.dataframe(df_local, use_container_width=True)
                else: st.warning("No se hallaron resultados en este PDF.")
