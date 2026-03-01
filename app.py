import streamlit as st
import pdfplumber
import openai

# 1. CONFIGURACIÓN DE INTERFAZ
st.set_page_config(page_title="Radar Legal PRO", page_icon="⚖️", layout="wide")

st.title("⚖️ Radar Legal Final: Costa Rica")
st.markdown("---")

# 2. BARRA LATERAL - SEPARACIÓN DE MÓDULOS
with st.sidebar:
    st.header("⚙️ Configuración de Élite")
    api_key = st.text_input("OpenAI API Key", type="password")
    
    # Separación lógica de programas según tus instrucciones
    materia = st.radio("Seleccione el Módulo:", ["Cobro Judicial", "Radar Penal"])
    
    st.divider()
    if materia == "Cobro Judicial":
        st.info("Módulo Cobro: Prescripción y Caducidad.")
    else:
        st.info("Módulo Radar: Nulidades Art. 178/181 CPP.")

# 3. CARGA DE EXPEDIENTE
archivo = st.file_uploader(f"Subir documento para {materia} (PDF)", type=["pdf"])

if archivo and api_key:
    with st.spinner(f"Ejecutando motor de {materia}..."):
        texto_completo = ""
        try:
            with pdfplumber.open(archivo) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t: texto_completo += t + "\n"
            
            client = openai.OpenAI(api_key=api_key)

            # --- LÓGICA POR MATERIA ---
            if materia == "Cobro Judicial":
                prompt_instruccion = "Experto en COBRO JUDICIAL CR. Analizá: 1. Prescripción (Código Comercio), 2. Caducidad procesal, 3. Título ejecutivo."
            else:
                prompt_instruccion = "Experto en PENAL CR. Analizá: 1. Nulidades (Art. 178 CPP), 2. Prueba espuria (Art. 181 CPP), 3. Tipicidad."

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"IA Jurídica de Alto Impacto. Módulo: {materia}. Solo leyes de Costa Rica."},
                    {"role": "user", "content": f"{prompt_instruccion}\n\nTEXTO:\n{texto_completo[:15000]}"}
                ],
                temperature=0.1
            )

            analisis_final = response.choices[0].message.content
            st.subheader(f"📊 Dictamen Especializado: {materia}")
            st.markdown(analisis_final)

            st.divider()

            # 4. GENERACIÓN DE DOCUMENTOS
            st.subheader("📝 Generación de Escritos")
            
            label_doc = "🛡️ Crear Excepción Prescripción/Caducidad" if materia == "Cobro Judicial" else "🚩 Crear Recurso de Apelación"
            
            if st.button(label_doc):
                with st.spinner("Redactando..."):
                    res_doc = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "Abogado litigante senior de Costa Rica."},
                            {"role": "user", "content": f"Redactá un documento formal de {label_doc} basado en: {analisis_final}"}
                        ]
                    )
                    st.text_area("Borrador para copiar:", value=res_doc.choices[0].message.content, height=500)
        
        except Exception as e:
            st.error(f"Error técnico: {e}")

elif not api_key and archivo:
    st.warning("⚠️ Ingresá la API Key para activar el motor.")
