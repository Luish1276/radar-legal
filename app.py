import streamlit as st
import pdfplumber
import openai

st.set_page_config(page_title="Radar Legal PRO", page_icon="⚖️", layout="wide")

st.title("⚖️ Radar Legal: Defensa Técnica de Alto Impacto")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Configuración de Combate")
    api_key = st.text_input("OpenAI API Key", type="password")
    materia = st.radio("Módulo Activo:", ["Radar Penal", "Cobro Judicial"])
    
    st.divider()
    if materia == "Radar Penal":
        nivel_penal = st.select_slider(
            "Perfil del Defensor:",
            options=["Abogado Litigante Senior", "Especialista en Casación", "Estratega de Defensa Criminal"]
        )
    else:
        st.info("📌 Módulo Cobro: Análisis de Prescripción, Caducidad y Notificaciones.")

archivo = st.file_uploader(f"Subir Expediente para {materia}", type=["pdf"])

if archivo and api_key:
    with st.spinner("🕵️ El Defensor está despedazando el expediente..."):
        texto_completo = ""
        with pdfplumber.open(archivo) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t: texto_completo += t + "\n"
        
        client = openai.OpenAI(api_key=api_key)

        # --- MOTOR RADAR PENAL: EL DEFENSOR AGRESIVO ---
        if materia == "Radar Penal":
            instruccion = f"""
            Actúa como un {nivel_penal} de Costa Rica, con enfoque de DEFENSA TÉCNICA AGRESIVA.
            Tu objetivo es ANULAR la pieza acusatoria o la sentencia. 
            Analiza el documento buscando:
            1. VICIOS PROCESALES (Art. 178 CPP): No los menciones, EXPLICÁ cómo afectan el derecho de defensa.
            2. PRUEBA ESPURIA (Art. 181 CPP): Buscá violaciones a la cadena de custodia o derechos fundamentales. Cita la doctrina del 'Fruto del Árbol Ponzoñoso'.
            3. FUNDAMENTACIÓN INTELECTIVA: Detectá si el juez usó 'machotes' o si hay contradicciones lógicas (vicios de la voluntad).
            4. JURISPRUDENCIA: Cita votos de la SALA TERCERA sobre el debido proceso y la duda metódica (In Dubio Pro Reo).
            5. ESTRATEGIA: Decime qué incidente o recurso presentar YA para frenar el proceso.
            """
            perfil_sys = f"Sos un {nivel_penal} experto en derribar acusaciones del Ministerio Público en Costa Rica."

        # --- MOTOR COBRO JUDICIAL: EL ESTRATEGA MERCANTIL ---
        else:
            instruccion = """
            Actúa como un Abogado Defensor en Cobro Judicial.
            1. PRESCRIPCIÓN Y CADUCIDAD: Buscá la liberación de la deuda (Art. 968 C.Com y Art. 55 Ley Cobro).
            2. NOTIFICACIONES: Buscá vicios en el emplazamiento según la Ley 8687 para anular todo lo actuado.
            3. USURA: Analizá si los intereses pactados violan la Ley de Usura.
            """
            perfil_sys = "Experto en litigio civil y mercantil de Costa Rica."

        res_analisis = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": perfil_sys},
                {"role": "user", "content": f"{instruccion}\n\nEXPEDIENTE:\n{texto_completo[:18000]}"}
            ],
            temperature=0.2
        )
        analisis_texto = res_analisis.choices[0].message.content
        st.subheader(f"📊 Dictamen de la Defensa: {materia}")
        st.markdown(analisis_texto)

        st.divider()

        # --- GENERADOR DE RECURSOS DE ALTO IMPACTO ---
        st.subheader("📝 Redacción de Escritos de Combate")
        
        if materia == "Radar Penal":
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚩 Redactar Apelación de Sentencia"):
                    prompt_doc = f"Redactá un RECURSO DE APELACIÓN de nivel {nivel_penal}. Atacá la valoración de la prueba y citá jurisprudencia de la Sala Tercera. Análisis base: {analisis_texto}"
                    res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt_doc}])
                    st.text_area("Borrador de Apelación:", value=res.choices[0].message.content, height=500)
            with col2:
                if st.button("🚫 Redactar Incidente de Nulidad"):
                    prompt_doc = f"Redactá un INCIDENTE DE NULIDAD ABSOLUTA por vicios en el debido proceso (Art. 178 CPP). Análisis: {analisis_texto}"
                    res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt_doc}])
                    st.text_area("Borrador de Nulidad:", value=res.choices[0].message.content, height=500)
        
        else:
            if st.button("🛡️ Redactar Oposición y Excepciones"):
                prompt_doc = f"Redactá una oposición formal a la ejecución cobratoria con excepciones de prescripción y nulidad de notificación. Análisis: {analisis_texto}"
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt_doc}])
                st.text_area("Escrito de Cobro:", value=res.choices[0].message.content, height=500)

elif not api_key and archivo:
    st.warning("⚠️ Ingresá la API Key para activar la defensa.")
