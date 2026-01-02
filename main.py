import streamlit as st
import pdfplumber
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime

# 1. Configuración de la página (Primera línea de ejecución)
st.set_page_config(page_title="Radar Legal CR", layout="wide", page_icon="⚖️")

# 2. Título de la App
st.title("⚖️ Radar Legal Avanzado - Costa Rica")
st.markdown("---")

# 3. Función de búsqueda
def buscar_en_archivo(contenido_pdf, palabras_clave):
    try:
        with pdfplumber.open(BytesIO(contenido_pdf)) as pdf:
            resultados = []
            for i, pagina in enumerate(pdf.pages):
                texto = pagina.extract_text()
                if texto:
                    for palabra in palabras_clave:
                        if palabra and palabra.lower() in texto.lower():
                            inicio = max(0, texto.lower().find(palabra.lower()) - 100)
                            fin = inicio + 250
                            contexto = "..." + texto[inicio:fin] + "..."
                            resultados.append({
                                "Página": i + 1,
                                "Categoría/Palabra": palabra,
                                "Extracto": contexto.replace("\n", " ")
                            })
            return pd.DataFrame(resultados), None
    except Exception as e:
        return None, f"Error al procesar el PDF: {str(e)}"

# 4. Barra Lateral
st.sidebar.header("📅 Configuración de Fecha")
fecha_consulta = st.sidebar.date_input("Seleccione fecha:", datetime.now())
fecha_str = fecha_consulta.strftime("%d/%m/%Y")

dia, mes, anio = fecha_consulta.strftime("%d"), fecha_consulta.strftime("%m"), fecha_consulta.strftime("%Y")
url_boletin = f"https://www.imprentanacional.go.cr/boletin/?date={dia}/{mes}/{anio}"

# 5. Definición de Pestañas
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏛️ Remates", 
    "🚗 Lesiones", 
    "⚖️ Prescripciones", 
    "🔍 Consulta Cliente", 
    "📂 Analizar PDF Propio"
])

def ejecutar_busqueda_url(lista_palabras):
    with st.spinner("Buscando en la Imprenta Nacional..."):
        try:
            response = requests.get(url_boletin, timeout=15)
            if response.status_code != 200 or b'%PDF' not in response.content[:100]:
                st.info("No hay boletín disponible para esta fecha (Feriado o Fin de semana).")
                return
            
            df, error = buscar_en_archivo(response.content, lista_palabras)
            if error: st.error(error)
            elif not df.empty:
                st.success("¡Hallazgos encontrados!")
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No se encontraron resultados.")
        except:
            st.error("Error de conexión con el servidor de la Imprenta.")

# 6. Contenido de Pestañas
with tab1:
    if st.button("Buscar Remates Ahora"):
        ejecutar_busqueda_url(["Remate", "Primer remate"])

with tab2:
    if st.button("Buscar Casos de Tránsito"):
        ejecutar_busqueda_url(["Lesiones culposas", "Tránsito"])

with tab3:
    if st.button("Buscar Prescripciones Ahora"):
        ejecutar_busqueda_url(["Prescripción"])

with tab4:
    dato_cliente = st.text_input("Cédula o Nombre del Cliente:")
    if st.button("Rastrear Cliente"):
        if dato_cliente:
            ejecutar_busqueda_url([dato_cliente])
        else:
            st.error("Ingrese un dato.")

with tab5:
    st.subheader("Analizador Local")
    archivo_subido = st.file_uploader("Suba su PDF aquí", type="pdf")
    if archivo_subido and st.button("Analizar Archivo Subido"):
        df, error = buscar_en_archivo(archivo_subido.read(), ["Remate", "Cédula", "Prescripción"])
        if error: st.error(error)
        elif not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No se encontraron palabras clave.")
