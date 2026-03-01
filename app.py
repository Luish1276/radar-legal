import streamlit as st
import pdfplumber
import openai

# 1. CONFIGURACIÓN ESTRUCTURAL
st.set_page_config(page_title="Radar Legal PRO", page_icon="⚖️", layout="wide")

st.title("⚖️ Radar Legal: Inteligencia Jurídica de Alto Nivel")
st.markdown("---")

# 2. BARRA LATERAL (Aquí está tu Slider de vuelta)
with st.sidebar:
    st.header("⚙️ Configuración de Élite")
    api_key = st.text_input("OpenAI API Key", type="password")
    
    # Separación de programas
    materia = st.radio("Seleccione el Módulo:", ["Cobro Judicial", "Radar Penal"])
    
    st.divider()
    
    # EL SLIDER DE NIVEL PROFESIONAL QUE TE GUSTABA
    nivel_perfil = st.select_slider(
        "Nivel de Especialidad del Analista:",
        options=["Abogado Senior", "Especialista Avanzado", "Dr. en Derecho con Alta Experiencia"]
    )
    
    st.divider()
    st.info(f"Módulo: {materia}\nPerfil: {nivel_perfil}")

# 3. CARGA DE ARCHIVOS
archivo = st.file_uploader(f"Subir expediente para {materia} (PDF)", type=["pdf"])

if archivo and api_key:
    with st.spinner(f"🕵️ El {nivel_perfil} está analizando el caso..."):
        texto_completo = ""
        try:
            with pdfplumber.open(archivo) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t: texto_completo += t + "\n"
            
            client = openai.OpenAI(api_key=api_key)

            # --- LÓGICA DE ALTO IMPACTO SEPARADA ---
            if materia == "Cobro Judicial":
                instruccion = f"""
                Actuá como un {nivel_perfil} experto en Cobro Judicial de Costa Rica.
                Analizá con lupa:
                1. PRESCRIPCIÓN: Revisá vencimiento de títulos valores (Pagaré, Letra, Factura).
                2. CADUCIDAD: Revisá inactividad procesal para solicitar el archivo del expediente.
                3. TÍTULO: ¿Es idóneo según la Ley de Cobro Judicial?
                4. ESTRATEGIA: ¿Qué excepción es la más contundente?
                """
            else:
                instruccion = f"""
                Actuá como un {nivel_perfil} con amplia experiencia en Derecho Penal costarricense.
                Analizá profundamente:
                1. NULIDADES ABSOLUTAS: Buscá violaciones al debido proceso (Art. 178 CPP).
                2. VICIOS DE PRUEBA: Identificá prueba espuria o ilegalmente obtenida (Art. 181 CPP).
                3. MOTIVACIÓN: ¿La sentencia tiene vicios de fundamentación intelectual?
                4. TIPICIDAD Y DOGMÁTICA: ¿Calza el hecho con la teoría del delito?
                """

            # EJECUCIÓN DEL ANÁLISIS
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"Sos un {nivel_perfil} en Costa Rica. Tu análisis es técnico, profundo y crítico. No des resúmenes básicos."},
                    {"role": "user", "content": f"{instruccion}\n\nDOCUMENTO:\n{texto_completo[:15000]}"}
                ],
                temperature=0.2
            )

            analisis_texto = response.choices[0].message.content
            st.subheader(f"📊 Dictamen del {nivel_perfil} ({materia})")
            st.markdown(analisis_texto)

            st.divider()

            # 4. GENERACIÓN DE DOCUMENTOS (Apelaciones o Excepciones)
            st.subheader("📝 Generación de Escritos de Alto Impacto")
            
            btn_txt = "🛡️ Redactar Excepción de Prescripción" if materia == "Cobro Judicial" else "🚩 Redactar Recurso de Apelación"
            
            if st.button(btn_txt):
                with st.spinner(f"El {nivel_perfil} está redactando el escrito..."):
                    res_doc = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": f"Sos un {nivel_perfil} redactando para tribunales de Costa Rica. Usá lenguaje jurídico formal y contundente."},
                            {"role": "user", "content": f"Redactá un {btn_txt} basado en este análisis técnico: {analisis_texto}"}
                        ]
                    )
                    st.success("✅ Escrito jurídico generado.")
                    st.text_area("Documento listo para copiar:", value=res_doc.choices[0].message.content, height=600)

        except Exception as e:
            st.error(f"Error técnico en el motor: {e}")

elif not api_key and archivo:
    st.warning("⚠️ El motor de alta fidelidad requiere la API Key.")
