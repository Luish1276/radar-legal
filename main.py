import streamlit as st
import pdfplumber
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime

# 1. Configuración de la página
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
                        # Limpiamos espacios y verificamos que no esté vacío
                        p = palabra.strip()
                        if p and p.lower() in texto.lower():
                            inicio = max(0, texto.lower().find(p.lower()) - 100)
                            fin = inicio + 250
                            contexto = "..." + texto[inicio:fin] + "..."
                            resultados.append({
                                "Página": i + 1,
                                "Dato Encontrado": p,
                                "Extracto": contexto.replace("\n", " ")
                            })
            return pd.DataFrame(resultados), None
    except Exception as e:
        return None, f"Error al leer el PDF: {str(e)}"

# --- BARRA LATERAL (Para boletines automáticos) ---
st.sidebar.header("📅 Boletín de la Imprenta")
fecha_consulta = st.sidebar.date_input("Seleccione fecha:", datetime.now())
dia, mes, anio = fecha_consulta.strftime("%d"), fecha_consulta.strftime("%m"), fecha_consulta.strftime("%Y")
url_boletin = f"https://www.imprentanacional.go.cr/boletin/?date={dia}/{mes}/{anio}"

# --- PESTAÑAS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏛️ Remates", "🚗 Lesiones", "⚖️ Prescripciones", "🔍 Consulta Cliente", "📂 Analizar PDF Propio"
])

# Función para búsquedas automáticas (Tabs 1-4)
def ejecutar_busqueda_url(lista):
    with st.spinner("Buscando en la Imprenta..."):
        try:
            r = requests.get(url_boletin, timeout=15)
            if r.status_code != 200 or b'%PDF' not in r.content[:100]:
                st.info("No hay boletín disponible para esta fecha.")
                return
            df, err = buscar_en_archivo(r.content, lista)
            if df is not None and not df.empty:
                st.success(f"¡Hallazgos encontrados!")
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
    cliente = st.text_input("Nombre o Cédula (Automático):")
    if st.button("Rastrear en la Imprenta"): ejecutar_busqueda_url([cliente])

# --- MEJORA EN LA PESTAÑA 5: ANALIZADOR DE ARCHIVOS PROPIOS ---
with tab5:
    st.subheader("📂 Analizador de Boletines y Documentos Locales")
    st.write("Use esta pestaña para escanear archivos que ya descargó o boletines de años anteriores.")
    
    archivo_subido = st.file_uploader("Subir PDF", type="pdf")
    
    col1, col2 = st.columns(2)
    with col1:
        cedula_local = st.text_input("Cédula o Nombre a buscar:")
    with col2:
        otras_palabras = st.text_input("Otras palabras (ej: Remate, Finca):")
    
    if archivo_subido is not None:
        if st.button("🚀 Iniciar Escaneo de Archivo"):
            with st.spinner("Escaneando documento..."):
                bytes_data = archivo_subido.getvalue()
                
                # Creamos la lista de búsqueda combinando cédula y otras palabras
                lista_busqueda = [cedula_local, otras_palabras]
                # Filtramos para quitar espacios vacíos
                lista_busqueda = [x for x in lista_busqueda if x.strip()]
                
                df_local, error_local = buscar_en_archivo(bytes_data, lista_busqueda)
                
                if error_local:
                    st.error(error_local)
                elif df_local is not None and not df_local.empty:
                    st.success(f"¡Encontrado! Se detectaron {len(df_local)} coincidencias.")
                    st.dataframe(df_local, use_container_width=True)
                else:
                    st.warning("No se encontró la cédula ni las palabras clave en este archivo.")
¿Qué agregamos nuevo?
