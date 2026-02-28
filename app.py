import streamlit as st
import pdfplumber
import openai

st.set_page_config(page_title="Radar Legal CR", page_icon="⚖️", layout="wide")

st.title("⚖️ Radar Legal Final: Costa Rica")
st.markdown("---")

# Barra lateral con opciones
with st.sidebar:
    st.header("⚙️ Panel de Control")
    api_key = st.text_input("OpenAI API Key", type="password")
    materia = st.selectbox("Materia del Expediente", ["Cobro Judicial", "Penal", "Laboral"])
    st.info("Seleccioná la materia para que el Radar aplique la ley correcta.")

# Carga de archivo
archivo = st.file_uploader("Subir Expediente o Documento (PDF)", type=["pdf"])

# NUEVO: Cuadro para que vos escribás preguntas
pregunta_usuario = st.text_input("¿Qué querés saber específicamente de este documento?")

if archivo and api_key:
    with st.spinner("Procesando bajo legislación de Costa Rica..."):
        texto_exp = ""
        with pdfplumber.open(archivo) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t: texto_exp += t + "\n"
        
        # Lógica según materia
        if materia == "Cobro Judicial":
            instruccion = "Analiza este documento de COBRO JUDICIAL. Busca: Título ejecutivo, monto líquido, intereses moratorios y posible PRESCRIPCIÓN según el Código de Comercio de CR."
        elif materia == "Penal":
            instruccion = "Analiza este caso PENAL. Busca: Nulidades (Art. 178 CPP), vicios de prueba (Art. 181 CPP) y tipicidad según el Código Penal de CR."
        else:
            instruccion = "Analiza este caso LABORAL. Busca: Debido proceso administrativo y causales de despido injustificado."

        client = openai.OpenAI(api_key=api_key)
        
        # Unimos tu pregunta con la lógica legal
        prompt_completo = f"{instruccion}\n\nPregunta específica del abogado: {pregunta_usuario}\n\nTexto del documento: {texto_exp[:15000]}"
        
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Sos un consultor jurídico experto en Costa Rica."},
                      {"role": "user", "content": prompt_completo}]
        )
        
        st.subheader(f"🔍 Dictamen Radar: {materia}")
        st.markdown(res.choices[0].message.content)

elif not api_key and archivo:
    st.warning("⚠️ Ingresá la API Key en la barra lateral para iniciar el análisis.")
