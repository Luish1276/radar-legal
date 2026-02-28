import streamlit as st
import pdfplumber
import openai

st.set_page_config(page_title="Radar Legal CR", page_icon="⚖️")
st.title("⚖️ Radar Legal: Análisis Profundo (Costa Rica)")

with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input("OpenAI API Key", type="password")
    materia = st.selectbox("Materia", ["Penal", "Laboral", "Administrativo"])

archivo = st.file_uploader("Subir expediente (PDF)", type=["pdf"])

if archivo and api_key:
    with st.spinner("Analizando bajo leyes de Costa Rica..."):
        texto_exp = ""
        with pdfplumber.open(archivo) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t: texto_exp += t + "\n"
        
        client = openai.OpenAI(api_key=api_key)
        prompt = f"Analiza este caso de Costa Rica: {texto_exp[:10000]}"
        
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Experto legal CR."},
                      {"role": "user", "content": prompt}]
        )
        st.subheader("🔍 Dictamen del Radar")
        st.write(res.choices[0].message.content)
elif not api_key and archivo:
    st.warning("Por favor, ingresa tu API Key.")  
