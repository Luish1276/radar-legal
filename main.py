import streamlit as st
import pdfplumber
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Radar Legal CR", layout="wide")

st.title("⚖️ Radar Legal Avanzado - Costa Rica")
st.markdown("### Buscador Automatizado de Edictos y Notificaciones")

# --- LÓGICA DE BÚSQUEDA ---
def buscar_en_boletin(url, palabras_clave):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None, "No se pudo acceder al boletín de esta fecha."
        
        with pdfplumber.open(BytesIO(response.content)) as pdf:
            resultados = []
            for i, pagina in enumerate(pdf.pages):
                texto = pagina.extract_text()
                if texto:
                    for palabra in palabras_clave:
                        if palabra.lower() in texto.lower():
                            # Extraemos un contexto del hallazgo
                            inicio = max(0, texto.lower().find(palabra.lower()) - 100)
                            fin = inicio + 250
                            contexto = "..." + texto[inicio:fin] + "..."
                            resultados.append({
                                "Página": i + 1,
                                "Categoría": palabra,
                                "Hallazgo": contexto.replace("\n", " ")
                            })
            return pd.DataFrame(resultados), None
    except Exception as e:
        return None, f"Error: {str(e)}"

# --- INTERFAZ ---
# Creamos 4 pestañas
tab1, tab2, tab3, tab4 = st.tabs(["🏛️ Remates", "🚗 Lesiones", "⚖️ Prescripciones", "🔍 Histórico/Cédula"])

# Selector de fecha global para todas las consultas
st.sidebar.header("Configuración de Fecha")
fecha_consulta = st.sidebar.date_input("Seleccione la fecha a consultar:", datetime.now())
fecha_str = fecha_consulta.strftime("%d/%m/%Y")
# Construcción de URL de la Imprenta (Formato estándar)
dia = fecha_consulta.strftime("%d")
mes = fecha_consulta.strftime("%m")
anio = fecha_consulta.strftime("%Y")
url_boletin = f"https://www.imprentanacional.go.cr/boletin/?date={dia}/{mes}/{anio}"

with tab1:
    st.header("Búsqueda de Remates Judiciales")
    if st.button("Buscar Remates"):
        with st.spinner("Escaneando remates..."):
            df, error = buscar_en_boletin(url_boletin, ["Remate", "Primer remate", "Segunda publicación"])
            if error: st.error(error)
            elif not df.empty: st.dataframe(df)
            else: st.warning("No se hallaron remates en esta fecha.")

with tab2:
    st.header("Lesiones Culposas")
    if st.button("Buscar Accidentes/Lesiones"):
        with st.spinner("Buscando expedientes..."):
            df, error = buscar_en_boletin(url_boletin, ["Lesiones culposas", "Accidente", "Tránsito"])
            if error: st.error(error)
            elif not df.empty: st.dataframe(df)
            else: st.warning("No se hallaron casos registrados.")

with tab3:
    st.header("Prescripciones")
    if st.button("Buscar Prescripciones"):
        with st.spinner("Analizando edictos..."):
            df, error = buscar_en_boletin(url_boletin, ["Prescripción", "Interrupción de la prescripción"])
            if error: st.error(error)
            elif not df.empty: st.dataframe(df)
            else: st.warning("Sin resultados.")

with tab4:
    st.header("🔍 Consulta de Cliente (Histórica)")
    st.info("Utilice esta pestaña para buscar un nombre o cédula específica en un boletín de cualquier fecha.")
    
    dato_cliente = st.text_input("Ingrese Cédula (con o sin guiones) o Nombre completo:")
    
    if st.button("Rastrear en Fecha Seleccionada"):
        if dato_cliente:
            with st.spinner(f"Buscando '{dato_cliente}' en el boletín del {fecha_str}..."):
                df, error = buscar_en_boletin(url_boletin, [dato_cliente])
                if error: 
                    st.error(error)
                elif not df.empty: 
                    st.success(f"¡HALLAZGO! Se encontró mención de '{dato_cliente}' en la página {df['Página'].iloc[0]}")
                    st.dataframe(df)
                else: 
                    st.warning(f"No aparece '{dato_cliente}' en el boletín del {fecha_str}.")
        else:
            st.error("Debe ingresar un dato para buscar.")

st.sidebar.markdown(f"**Consultando:** {fecha_str}")
st.sidebar.info("Nota: Los boletines de fin de semana o feriados podrían no estar disponibles.")
