import streamlit as st
import pdfplumber
import openai

# ESTA ES LA LÍNEA 4 - Ahora está protegida por la importación correcta arriba
st.set_page_config(page_title="Radar Legal PRO", page_icon="⚖️", layout="wide")

st.title("⚖️ Radar Legal: Inteligencia Jurídica y Redacción")
st.markdown("---")

# Barra lateral
with st.sidebar:
    st.header("⚙️ Motor de Análisis")
    api_key = st.text_input("OpenAI API Key", type="password")
    materia = st.radio("Materia del Caso:", ["Penal", "Cobro Judicial"])
    nivel = st.select_slider("Profundidad de Redacción:", options=["Básico", "Avanzado", "Casación"])

archivo = st.file_uploader("Subir Sentencia o Resolución (PDF)", type=["pdf"])

if archivo and api_key:
    with st.spinner("⚖️ Procesando expediente..."):
        texto_completo = ""
        try:
            with pdfplumber.open(archivo) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t: texto_completo += t + "\n"
            
            client = openai.OpenAI(api_key=api_key)
            
            # PASO 1: Análisis Automático
            st.subheader("🔍 Análisis de Hallazgos y Agravios")
            
            prompt_analisis = f"Actúa como un experto legal en Costa Rica. Analiza esta sentencia de materia {materia} y detecta 3 errores graves (procesales o de fondo) que sean apelables bajo leyes de CR. Texto: {texto_completo[:15000]}"
            
            analisis_res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "Analista jurídico de Costa Rica de alto nivel."},
                          {"role": "user", "content": prompt_analisis}]
            )
            analisis_texto = analisis_res.choices[0].message.content
            st.markdown(analisis_texto)

            st.markdown("---")
            
            # PASO 2: El Botón para la Apelación
            st.subheader("📝 Generador de Documentos")
            if st.button(f"Generar Recurso de Apelación ({materia})"):
                with st.spinner("Redactando recurso formal..."):
                    prompt_apelacion = f"""
                    Redacta un RECURSO DE APELACIÓN formal para Costa Rica (Materia: {materia}).
                    ESTRUCTURA OBLIGATORIA:
                    1. Encabezamiento formal tico.
                    2. AGRAVIOS: Basate en estos hallazgos: {analisis_texto}.
                    3. FUNDAMENTACIÓN: Cita leyes de CR (CPP o Código de Comercio/Cobro).
                    4. PETITORIA: Solicita revocatoria o nulidad.
                    Documento: {texto_completo[:10000]}
                    """
                    
                    apelacion_res = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "system", "content": "Sos un abogado litigante experto en Costa Rica."},
                                  {"role": "user", "content": prompt_apelacion}]
                    )
                    
                    st.success("✅ Recurso Generado")
                    st.text_area("Borrador para copiar a Word:", value=apelacion_res.choices[0].message.content, height=600)
        except Exception as e:
            st.error(f"Error al leer el PDF: {e}")

elif not api_key and archivo:
    st.warning("⚠️ Ingresá la API Key para activar el motor.")
