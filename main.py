import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO

# 1. Configuración de la página
st.set_page_config(page_title="Radar Legal Pro", layout="wide", page_icon="⚖️")

st.title("⚖️ Radar Legal: Cobro Judicial y Subastas")

# --- LÓGICA DE MEMORIA (Session State) ---
# Esto permite que el PDF subido persista entre pestañas
if 'pdf_data' not in st.session_state:
    st.session_state['pdf_data'] = None

# --- MOTOR DE BÚSQUEDA CON FILTROS DE EXCLUSIÓN ---
def procesar_pdf_profesional(contenido_pdf, palabras_clave, excluir=None):
    if excluir is None:
        excluir = []
    
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
                                # Verificamos si hay palabras prohibidas (como 'Municipalidad')
                                contexto_breve = linea.lower()
                                if any(exc.lower() in contexto_breve for exc in excluir):
                                    continue # Salta este hallazgo si es municipal
                                
                                # Si pasa el filtro, capturamos el bloque de 18 líneas
                                inicio = max(0, index - 2) # Un par de líneas antes para contexto
                                fin = min(len(lineas), index + 16)
                                bloque = "\n".join(lineas[inicio:fin])
                                
                                resultados.append({
                                    "Página": i + 1,
                                    "Hallazgo": palabra,
                                    "CONTENIDO DEL EDICTO": bloque
                                })
            return pd.DataFrame(resultados)
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

# --- BARRA LATERAL: CARGA ÚNICA ---
st.sidebar.header("📂 Archivo del Día")
archivo_subido = st.sidebar.file_uploader("Suba el PDF aquí (una sola vez):", type="pdf")

if archivo_subido:
    st.session_state['pdf_data'] = archivo_subido.getvalue()
    st.sidebar.success("✅ PDF cargado y listo para todas las pestañas.")
else:
    st.sidebar.warning("⚠️ Esperando archivo...")

# --- PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🏛️ Remates y Subastas", "💰 Cobro Judicial (No Municipal)", "🚗 Tránsito", "🔍 Cliente Específico"
])

def mostrar_seccion(keywords, titulo, exclusiones=None):
    if st.session_state['pdf_data'] is not None:
        df = procesar_pdf_profesional(st.session_state['pdf_data'], keywords, exclusiones)
        if not df.empty:
            st.success(f"Se encontraron {len(df)} coincidencias en {titulo}")
            for _, row in df.iterrows():
                with st.expander(f"📄 Página {row['Página']} | Detectado: {row['Hallazgo']}"):
                    st.text(row['CONTENIDO DEL EDICTO'])
        else:
            st.warning(f"No hay resultados para {titulo} en este archivo.")
    else:
        st.info("Por favor, suba un PDF en la barra lateral para ver los datos.")

with tab1:
    # Agregamos 'Subasta' y términos relacionados con fechas de remate
    if st.button("Ver Remates y Subastas"):
        mostrar_seccion(["Remate", "Subasta", "continuar sin oferentes", "señalan las"], "Remates")

with tab2:
    # Filtramos explícitamente lo Municipal
    if st.button("Ver Cobros Judiciales"):
        mostrar_seccion(
            ["Cobro Judicial", "Embargo", "Decretado", "Mandamiento", "Monitorio"], 
            "Cobros", 
            excluciones=["Municipalidad", "Municipal", "Patentes", "Impuestos municipales"]
        )

with tab3:
    if st.button("Ver Tránsito"):
        mostrar_seccion(["Lesiones culposas", "Tránsito", "Colisión"], "Tránsito")

with tab4:
    cliente = st.text_input("Cédula o Nombre:")
    if st.button("Rastrear"):
        if cliente:
            mostrar_seccion([cliente], f"Cliente: {cliente}")
