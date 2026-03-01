import streamlit as st
import pdfplumber
import openai

st.set_page_config(page_title="Radar Legal PRO", page_icon="⚖️", layout="wide")

st.title("⚖️ Radar Legal: Inteligencia Jurídica Especializada")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Selección de Programa")
    api_key = st.text_input("OpenAI API Key", type="password")
    materia = st.radio("Módulo Activo:", ["Cobro Judicial", "Radar Penal"])
    
    st.divider()
    if materia == "Radar Penal":
        nivel_penal = st.select_slider(
            "Perfil del Analista Penal:",
            options=["Consultor Senior", "Especialista en Casación", "Dr. en Derecho Penal"]
        )
    else:
        st.info("📌 Módulo Cobro: Análisis de Prescripción, Caducidad y Validez de Notificaciones (Ley 8687).")

archivo = st.file_uploader(f"Subir Expediente para {materia}", type=["pdf"])

if archivo and api_key:
    with st.spinner("🕵️ Realizando escaneo sustantivo y procesal..."):
        texto_completo = ""
        with pdfplumber.open(archivo) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t: texto_completo += t + "\n"
        
        client = openai.OpenAI(api_key=api_key)

        if materia == "Cobro Judicial":
            instruccion = """
            Actúa como un Juez de Cobro de Costa Rica con enfoque en Debido Proceso.
            Realiza un ANÁLISIS SUSTANTIVO Y PROCESAL:
            1. TÍTULO: Requisitos de ejecutoriedad (Código de Comercio).
            2. PRESCRIPCIÓN Y CADUCIDAD: Fechas críticas y Art. 55 Ley Cobro.
            3. CONTROL DE NOTIFICACIÓN (CRÍTICO): 
               - Analiza si la notificación cumple con la Ley de Notificaciones Judiciales (Ley 8687).
               - Verifica si el acta de notificación identifica correctamente al receptor (Art. 7).
               - Revisa si se respetó el domicilio contractual o si hubo vicio en la notificación automática (Art. 11).
               - Evalúa si el plazo de emplazamiento del CPC fue respetado antes de cualquier resolución de rebeldía o apremio.
            4. DEFENSAS PROCESALES: Identifica nulidades por falta de emplazamiento válido.
            """
            perfil_sys = "Experto en Procesal Civil y Ley de Notificaciones de Costa Rica."
        else:
            instruccion = f"Actúa como un {nivel_penal}. Analiza nulidades Art. 178 y 181 CPP."
            perfil_sys = f"Sos un {nivel_penal} experto en casación."

        res_analisis = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": perfil_sys},
                {"role": "user", "content": f"{instruccion}\n\nEXPEDIENTE:\n{texto_completo[:18000]}"}
            ],
            temperature=0.2
        )
        analisis_texto = res_analisis.choices[0].message.content
        st.subheader(f"📊 Dictamen Especializado: {materia}")
        st.markdown(analisis_texto)

        st.divider()

        # GENERADOR DE DOCUMENTOS (Ahora con Nulidad de Notificación)
        st.subheader("📝 Generación de Piezas Procesales")
        
        if materia == "Cobro Judicial":
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🛡️ Redactar Excepción de Prescripción"):
                    prompt_doc = f"Redacta una EXCEPCIÓN DE PRESCRIPCIÓN robusta basada en: {analisis_texto}. Cita Art. 968 C.Comercio."
                    res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt_doc}])
                    st.text_area("Borrador:", value=res.choices[0].message.content, height=400)
            with col2:
                if st.button("🚫 Redactar Incidente de Nulidad de Notificación"):
                    prompt_doc = f"Redacta un INCIDENTE DE NULIDAD DE NOTIFICACIÓN bajo la Ley 8687 y el CPC de Costa Rica, basado en los vicios detectados aquí: {analisis_texto}."
                    res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt_doc}])
                    st.text_area("Borrador Nulidad:", value=res.choices[0].message.content, height=400)
        
        else:
            if st.button(f"🚩 Redactar Recurso ({nivel_penal})"):
                prompt_doc = f"Redacta un Recurso de Apelación penal basado en: {analisis_texto}"
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt_doc}])
                st.text_area("Borrador Recurso:", value=res.choices[0].message.content, height=500)

elif not api_key and archivo:
    st.warning("⚠️ Ingresa la API Key para activar el Radar.")
