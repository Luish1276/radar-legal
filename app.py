import streamlit as st
import pdfplumber
import openai

# 1. CONFIGURACIÓN DE INTERFAZ
st.set_page_config(page_title="Radar Legal PRO", page_icon="⚖️", layout="wide")

st.title("⚖️ Radar Legal: Inteligencia Jurídica Especializada")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input("OpenAI API Key", type="password")
    
    # Separación estricta de programas
    materia = st.radio("Módulo Activo:", ["Radar Penal", "Cobro Judicial"])
    
    st.divider()
    if materia == "Radar Penal":
        # RESTAURAMOS TUS NIVELES EXACTOS
        nivel_penal = st.select_slider(
            "Perfil del Defensor:",
            options=["Abogado Litigante Senior", "Especialista en Casación", "Estratega de Defensa Criminal"]
        )
    else:
        st.info("📌 Módulo Cobro: Análisis de Prescripción, Caducidad, Usura y Nulidad de Emplazamiento (Ley 8687).")

# 2. CARGA DE ARCHIVOS
archivo = st.file_uploader(f"Subir Expediente para {materia}", type=["pdf"])

if archivo and api_key:
    with st.spinner("🕵️ Analizando expediente con rigor jurídico..."):
        texto_completo = ""
        with pdfplumber.open(archivo) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t: texto_completo += t + "\n"
        
        client = openai.OpenAI(api_key=api_key)

        # --- MOTOR 1: RADAR PENAL (CON TUS PERFILES EXACTOS) ---
        if materia == "Radar Penal":
            instruccion = f"""
            Actúa como un {nivel_penal} de Costa Rica con enfoque de DEFENSA TÉCNICA AGRESIVA.
            Analiza el documento buscando:
            1. NULIDADES ABSOLUTAS: Art. 178 CPP (Violación al debido proceso).
            2. PRUEBA ESPURIA: Art. 181 CPP (Vicios en obtención o cadena de custodia).
            3. MOTIVACIÓN: Vicios de fundamentación intelectiva en la sentencia.
            4. JURISPRUDENCIA: Cita votos de la SALA TERCERA que obliguen a la nulidad.
            Responde como el estratega que eres, indicando dónde está el error del MP o del Juez.
            """
            perfil_sys = f"Sos un {nivel_penal} experto en derribar casos penales en Costa Rica."

        # --- MOTOR 2: COBRO JUDICIAL (ANÁLISIS DE SOCIO SENIOR) ---
        else:
            instruccion = """
            Actúa como un Abogado Litigante Senior en Cobro Judicial (Costa Rica).
            ANALIZA Y RESPONDE COMO ABOGADO, NO EXPLIQUES LA LEY:
            1. NULIDAD DE NOTIFICACIÓN: Revisa el acta vs Ley 8687. ¿Se notificó en casa de habitación sin ser el lugar pactado? ¿Se identificó al receptor?
            2. PRESCRIPCIÓN: Indica si operó el Art. 968 C.Com (4 años) analizando la última gestión válida.
            3. CADUCIDAD: Revisa inactividad de 3 meses (Art. 55 Ley Cobro).
            4. USURA: Calcula la tasa anual. Si supera el límite del BCCR, dicta la nulidad de la cláusula.
            """
            perfil_sys = "Abogado Especialista en Litigio Mercantil y Procesal Civil (CR)."

        res_analisis = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": perfil_sys},
                {"role": "user", "content": f"{instruccion}\n\nEXPEDIENTE:\n{texto_completo[:18000]}"}
            ],
            temperature=0.2
        )
        
        st.subheader(f"📊 Dictamen de Alto Impacto: {materia}")
        st.markdown(res_analisis.choices[0].message.content)

        st.divider()

        # --- GENERADOR DE ESCRITOS ---
        st.subheader("📝 Generación de Escritos de Combate")
        
        if materia == "Radar Penal":
            if st.button(f"🚩 Redactar Recurso de {nivel_penal}"):
                prompt_doc = f"Redacta un RECURSO técnico y contundente basado en estos agravios: {res_analisis.choices[0].message.content}. Cita votos de la Sala Tercera."
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt_doc}])
                st.text_area("Borrador del Recurso:", value=res.choices[0].message.content, height=600)
        else:
            if st.button("🛡️ Redactar Oposición, Prescripción y Nulidad de Notificación"):
                prompt_doc = f"Redacta una OPOSICIÓN formal para Juzgado de Cobro. Incluye nulidad de notificación (Ley 8687), prescripción (Art. 968 C.Com) y nulidad por usura. Basado en: {res_analisis.choices[0].message.content}"
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt_doc}])
                st.text_area("Escrito de Cobro Listo:", value=res.choices[0].message.content, height=600)

elif not api_key and archivo:
    st.warning("⚠️ Inserte su API Key para activar el Radar.")
