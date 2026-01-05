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

# --- BARRA LATERAL ---
st.sidebar.header("📅 Boletín de la Imprenta")
fecha_consulta = st.sidebar.date_input("Seleccione fecha:", datetime.now())
dia, mes, anio = fecha_consulta.strftime("%d"), fecha_consulta.strftime("%m"), fecha_consulta.strftime("%Y")
url_boletin = f"https://www.imprentanacional.go.cr/boletin/?date={dia}/{mes}/{anio}"

# --- PESTAÑAS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏛️ Remates", "🚗 Lesiones", "⚖️ Prescripciones", "🔍 Consulta Cliente", "📂 Analizar PDF Propio"
])

def ejecutar_busqueda_url(lista, nombre_busqueda):
    with st.spinner(f"Buscando {nombre_busqueda} en la Imprenta Nacional..."):
        try:
            r = requests.get(url_boletin, timeout=15)
            # CASO 1: El archivo no existe en la web
            if r.status_code != 200 or b'%PDF' not in r.content[:100]:
                st.info(f"📅 El Boletín Judicial del {dia}/{mes}/{anio} no está disponible en el servidor de la Imprenta (posible feriado o fin de semana).")
                return
            
            # CASO 2: El archivo existe, procedemos a buscar
            df, err = buscar_en_archivo(r.content, lista)
            
            if err:
                st.error(f"Hubo un problema técnico al leer el archivo: {err}")
            elif df is not None and not df.empty:
                st.success(f"✅ ¡Hallazgo confirmado! Se encontró información relacionada.")
                st.dataframe(df, use_container_width=True)
            else:
                # CASO 3: El archivo existe pero la palabra/cédula NO está
                st.warning(f"🔍 Búsqueda completada: No se encontró ninguna mención de '{', '.join(lista)}' en el boletín del {dia}/{mes}/{anio}.")
        except:
            st.error("Error de conexión: No se pudo contactar con la Imprenta Nacional.")

with tab1:
    if st.button("Buscar Remates"): ejecutar_busqueda_url(["Remate", "Primer remate"], "Remates")
with tab2:
    if st.button("Buscar Lesiones"): ejecutar_busqueda_url(["Lesiones culposas", "Tránsito"], "Lesiones")
with tab3:
    if st.button("Buscar Prescripciones"): ejecutar_busqueda_url(["Prescripción"], "Prescripciones")
with tab4:
    cliente = st.text_input("Nombre o Cédula (Automático):")
    if st.button("Rastrear en la Imprenta"): 
        if cliente:
            ejecutar_busqueda_url([cliente], "Cédula/Nombre")
        else:
            st.error("Por favor, ingrese una cédula o nombre.")

with tab5:
    st.subheader("📂 Analizador de Boletines y Documentos Locales")
    archivo_subido = st.file_uploader("Subir PDF", type="pdf")
    col1, col2 = st.columns(2)
    with col1: cedula_local = st.text_input("Cédula o Nombre a buscar:")
    with col2: otras_palabras = st.text_input("Otras palabras:")
    
    if archivo_subido is not None:
        if st.button("🚀 Iniciar Escaneo de Archivo"):
            with st.spinner("Escaneando..."):
                bytes_data = archivo_subido.getvalue()
                lista_busqueda = [x for x in [cedula_local, otras_palabras] if x.strip()]
                df_local, error_local = buscar_en_archivo(bytes_data, lista_busqueda)
                if df_local is not None and not df_local.empty:
                    st.success(f"¡Encontrado en el archivo subido!")
                    st.dataframe(df_local, use_container_width=True)
                else:
                    st.warning("No se encontró el dato en el documento analizado.")
