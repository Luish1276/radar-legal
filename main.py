import streamlit as st
import pdfplumber
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Radar Legal CR", layout="wide")

st.title("⚖️ Radar Legal Avanzado - Costa Rica")

# --- LÓGICA DE BÚSQUEDA MEJORADA ---
def buscar_en_boletin(url, palabras_clave):
    try:
        response = requests.get(url, timeout=10)
        # Verificamos si la respuesta es exitosa y si el contenido parece un PDF
        if response.status_code != 200 or b'%PDF' not in response.content[:100]:
            return None, "No hay un boletín oficial disponible para la fecha seleccionada. (Feriado, fin de semana o archivo no cargado aún)."
        
        with pdfplumber.open(BytesIO(response.content)) as pdf:
            resultados = []
            for i, pagina in enumerate(pdf.pages):
                texto = pagina.extract_text()
                if texto:
                    for palabra in palabras_clave:
                        if palabra.lower() in texto.lower():
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
        return None, f"Aviso: No se pudo procesar el documento de este día."

# --- INTERFAZ ---
st.sidebar.header("📅 Configuración de Fecha")
fecha_consulta = st.sidebar.date_input("Seleccione la fecha:", datetime.now())
fecha_str = fecha_consulta.strftime("%d/%m/%Y")

# URL Dinámica
dia, mes, anio = fecha_consulta.strftime("%d"), fecha_consulta.strftime("%m"), fecha_consulta.strftime("%Y")
url_boletin = f"https://www.imprentanacional.go.cr/boletin/?date={dia}/{mes}/{anio}"

tab1, tab2, tab3, tab4 = st.tabs(["🏛️ Remates", "🚗 Lesiones", "⚖️ Prescripciones", "🔍 Consulta de Cliente"])

with tab1:
    if st.button("Buscar Remates"):
        df, error = buscar_en_boletin(url_boletin, ["Remate", "Primer remate"])
        if error: st.info(error)
        elif not df.empty: st.dataframe(df)
        else: st.warning("No se hallaron remates.")

with tab2:
    if st.button("Buscar Accidentes"):
        df, error = buscar_en_boletin(url_boletin, ["Lesiones culposas", "Tránsito"])
        if error: st.info(error)
        elif not df.empty: st.dataframe(df)
        else: st.warning("Sin casos registrados.")

with tab3:
    if st.button("Buscar Prescripciones"):
        df, error = buscar_en_boletin(url_boletin, ["Prescripción"])
        if error: st.info(error)
        elif not df.empty: st.dataframe(df)
        else: st.warning("Sin resultados.")

with tab4:
    st.subheader("Buscador Histórico")
    dato_cliente = st.text_input("Nombre o Cédula:")
    if st.button("Rastrear Cliente"):
        if dato_cliente:
            df, error = buscar_en_boletin(url_boletin, [dato_cliente])
            if error: st.info(error)
            elif not df.empty:
                st.success(f"Encontrado en página {df['Página'].iloc[0]}")
                st.dataframe(df)
            else: st.warning("No aparece en esta fecha.")
