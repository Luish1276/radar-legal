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

# --- PESTAÑAS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏛️ Remates", "🚗 Lesiones", "⚖️ Prescripciones", "🔍 Consulta Cliente", "📂 Analizar PDF Propio"
])

def ejecutar_busqueda_url(lista, nombre_busqueda):
    # Intentamos la URL estándar de la Imprenta
    url_boletin = f"https://www.imprentanacional.go.cr/boletin/?date={dia}/{mes}/{anio}"
    
    with st.spinner(f"Accediendo al servidor de la Imprenta para el {dia}/{mes}/{anio}..."):
        try:
            r = requests.get(url_boletin, timeout=20)
            
            # Verificamos si el PDF es válido
            if r.status_code == 200 and b'%PDF' in r.content[:100]:
                df, err = buscar_en_archivo(r.content, lista)
                if df is not None and not df.empty:
                    st.success(f"✅ Hallazgos en {nombre_busqueda}")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning(f"🔍 No se encontró '{', '.join(lista)}' en el boletín de esta fecha.")
            else:
                # Si falla, damos una explicación más detallada
                st.error(f"⚠️ Archivo no encontrado.")
                st.info(f"""
                **Posibles razones:**
                1. El servidor de la Imprenta Nacional está caído temporalmente.
                2. La fecha seleccionada ({dia}/{mes}/{anio}) es fin de semana o feriado.
                3. El boletín aún no ha sido cargado (usualmente después de las 8:30 AM).
                """)
                st.write(f"Puedes intentar verificar manualmente aquí: [Enlace Directo]({url_boletin})")
        except:
            st.error("Error crítico de conexión. Verifique su internet.")

with tab1:
    if st.button("Buscar Remates"): ejecutar_busqueda_url(["Remate", "Primer remate"], "Remates")
with tab2:
    if st.button("Buscar Lesiones"): ejecutar_busqueda_url(["Lesiones culposas", "Tránsito"], "Lesiones")
with tab3:
    if st.button("Buscar Prescripciones"): ejecutar_busqueda_url(["Prescripción"], "Prescripciones")
with tab4:
    cliente = st.text_input("Nombre o Cédula:")
    if st.button("Rastrear Cliente"):
        if cliente: ejecutar_busqueda_url([cliente], "Cliente")
        else: st.error("Ingrese un dato.")

with tab5:
    st.subheader("📂 Analizador de Boletines Locales")
    archivo_subido = st.file_uploader("Si descargó el PDF manualmente, súbalo aquí:", type="pdf")
    cedula_local = st.text_input("Dato a buscar en el archivo subido:")
    if archivo_subido and st.button("Analizar PDF"):
        df_l, err_l = buscar_en_archivo(archivo_subido.getvalue(), [cedula_local])
        if df_l is not None and not df_l.empty:
            st.success("¡Encontrado!")
            st.dataframe(df_l)
        else: st.warning("No se encontró el dato en este PDF.")
