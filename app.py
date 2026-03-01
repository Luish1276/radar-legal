import pdfplumber
import openai

st.set_page_config(page_title="Radar Legal PRO", page_icon="⚖️", layout="wide")

st.title("⚖️ Radar Legal: Inteligencia Jurídica y Redacción de Recursos")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Motor de Análisis")
    api_key = st.text_input("OpenAI API Key", type="password")
    materia = st.radio("Materia del Caso:", ["Penal", "Cobro Judicial"])
    nivel = st.select_slider("Profundidad de Redacción:", options=["Básico", "Avanzado", "Casación"])

archivo = st.file_uploader("Subir Sentencia o Resolución (PDF)", type=["pdf"])

if archivo and api_key:
    with st.spinner("⚖️ Procesando expediente..."):
        texto_completo = ""
        with pdfplumber.open(archivo) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t: texto_completo += t + "\n"
        
        client = openai.OpenAI(api_key=api_key)
        
        # PASO 1: Análisis Automático
        st.subheader("🔍 Análisis de Hallazgos y Agravios")
        
        prompt_analisis = f"Actúa como un experto legal en Costa Rica. Analiza esta sentencia de materia {materia} y detecta 3 errores graves (procesales o de fondo) que sean apelables. Texto: {texto_completo[:15000]}"
        
        analisis_res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Analista jurídico tico."},
                      {"role": "user", "content": prompt_analisis}]
        )
        analisis_texto = analisis_res.choices[0].message.content
        st.markdown(analisis_texto)

        st.markdown("---")
        
        # PASO 2: El Botón Mágico para la Apelación
        st.subheader("📝 Generador de Documentos")
        if st.button(f"Generar Recurso de Apelación ({materia})"):
            with st.spinner("Redactando recurso formal..."):
                prompt_apelacion = f"""
                Redacta un RECURSO DE APELACIÓN formal para los tribunales de Costa Rica basado en esta materia: {materia}.
                USA ESTA ESTRUCTURA:
                1. Encabezamiento (Señor Juez, etc).
                2. Relación de Hechos.
                3. AGRAVIOS: Basate en estos hallazgos: {analisis_texto}.
                4. FUNDAMENTACIÓN JURÍDICA: Cita artículos del CPP (si es penal) o Código de Comercio/Ley de Cobro (si es cobro).
                5. PETITORIA: Solicita la nulidad o revocatoria.
                
                Documento base: {texto_completo[:10000]}
                """
                
                apelacion_res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "Sos un abogado litigante de élite en Costa Rica. Redactás con lenguaje técnico, formal y contundente."},
                              {"role": "user", "content": prompt_apelacion}]
                )
                
                st.success("✅ Recurso Generado")
                st.text_area("Borrador de la Apelación (Podés copiar y pegar):", 
                             value=apelacion_res.choices[0].message.content, height=600)

elif not api_key and archivo:
    st.warning("⚠️ Ingresá la API Key para activar el motor de redacción.")
