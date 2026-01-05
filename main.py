import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO

# 1. Configuración de la página
st.set_page_config(page_title="Radar Legal Pro", layout="wide", page_icon="⚖️")

st.title("⚖️ Radar Legal: Cobro Judicial y Subastas")

# --- LÓGICA DE MEMORIA (Session State) ---
if 'pdf_data' not in st.session_state:
    st.session_state['pdf_data'] = None

# --- MOTOR DE BÚSQUEDA CON FILTROS DE EXCLUSIÓN ---
def procesar_pdf_profesional(contenido_pdf, palabras_clave, exclusiones=None):
    # Aquí corregí el nombre de la variable para que coincida siempre
    if exclusiones is None:
        exclusiones = []
    
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
                                # FILTRO DE EXCLUSIÓN
                                contexto_breve = linea.lower()
                                if any(exc.lower() in contexto_breve for exc in exclusiones):
                                    continue 
                                
                                # CAPTURA DE BLOQUE
                                inicio = max(0, index - 2)
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

# --- BARRA LATERAL ---
st.sidebar.header("📂 Archivo del Día")
archivo_subido = st.sidebar.file_uploader("Suba el PDF aquí (una sola vez):", type="pdf")

if archivo_subido:
    st.session_state['pdf_data'] = archivo_subido.getvalue()
    st.sidebar.success("✅ PDF cargado y listo.")
else:
    st.sidebar.warning("⚠️ Esperando archivo...")

# --- PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🏛️ Remates y Subastas", "💰 Cobro Judicial (No Municipal)", "🚗 Tránsito", "🔍 Cliente Específico"
])

def mostrar_seccion(keywords, titulo, lista_exclusiones=None):
    if st.session_state['pdf_data'] is not None:
        # Llamamos a la función con el nombre correcto
        df = procesar_pdf_profesional(st.session_state['pdf_data'], keywords, exclusiones=lista_exclusiones)
        if not df.empty:
            st.success(f"Se encontraron {len(df)} coincidencias en {titulo}")
            for _, row in df.iterrows():
                with st.expander(f"📄 Página {row['Página']} | Detectado: {row['Hallazgo']}"):
                    st.text(row['CONTENIDO DEL EDICTO'])
        else:
            st.warning(f"No hay resultados para {titulo} en este archivo.")
    else:
        st.info("Por favor, suba un PDF en la barra lateral.")

with tab1:
    if st.button("Ver Remates y Subastas"):
        mostrar_seccion(["Remate", "Subasta", "continuar sin oferentes", "señalan las"], "Remates")

with tab2:
    if st.button("Ver Cobros Judiciales"):
        # Corregido: 'excluciones' -> 'lista_exclusiones'
        mostrar_seccion(
            ["Cobro Judicial", "Embargo", "Decretado", "Mandamiento", "Monitorio"], 
            "Cobros", 
            lista_exclusiones=["Municipalidad", "Municipal", "Patentes", "Impuestos municipales"]
        )

with tab3:
    if st.button("Ver Tránsito"):
        mostrar_seccion(["Lesiones culposas", "Tránsito", "Colisión"], "Tránsito")

with tab4:
    cliente = st.text_input("Cédula o Nombre:")
    if st.button("Rastrear"):
        if cliente:
            mostrar_seccion([cliente], f"Cliente: {cliente}")
