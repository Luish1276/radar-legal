import streamlit as st
import pdfplumber
import openai

st.set_page_config(page_title="Radar Legal PRO", page_icon="⚖️", layout="wide")

st.title("⚖️ Radar Legal: Especialización Jurídica Costa Rica")
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
        st.info("📌 Módulo Cobro: Análisis de Prescripción, Caducidad y Títulos Ejecutivos.")

archivo = st.file_uploader(f"Subir Expediente para {materia}", type=["pdf"])

if archivo and api_key:
    with st.spinner("🕵️ Analizando expediente con profundidad sustantiva..."):
        texto_completo = ""
        with pdfplumber.open(archivo) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t: texto_completo += t + "\n"
        
        client = openai.OpenAI(api_key=api_key)

        # --- MOTOR 1: COBRO JUDICIAL (Sin Slider, Enfoque Técnico-Legal) ---
        if materia == "Cobro Judicial":
            instruccion = """
            Actúa como un Juez Especializado en Cobro Judicial de Costa Rica.
            Realiza un ANÁLISIS SUSTANTIVO del expediente:
            1. TÍTULO: Identifica si es Pagaré, Letra o Factura. Verifica requisitos del Código de Comercio.
            2. CRONOLOGÍA DE PRESCRIPCIÓN: Extrae fecha de vencimiento, fecha de presentación de demanda y fechas de notificaciones.
            3. INTERRUPCIÓN: ¿Hubo gestiones cobratorias válidas? ¿Hay reconocimiento de deuda?
            4. CADUCIDAD: Revisa si el expediente estuvo paralizado por más de 3 meses (Art 55 Ley Cobro).
            5. CONCLUSIÓN: Determina con certeza si la obligación es exigible o si procede la excepción.
            """
            perfil_sys = "Experto en Derecho Mercantil y Procesal Civil de Costa Rica."

        # --- MOTOR 2: RADAR PENAL (Con Slider de Experiencia) ---
        else:
            instruccion = f"""
            Actúa como un {nivel_penal} en Costa Rica.
            Analiza profundamente la sentencia/expediente:
            1. NULIDADES ABSOLUTAS: Violaciones al Debido Proceso y Art. 178 CPP.
            2. PRUEBA ESPURIA: Vicios en la cadena de custodia o obtención (Art. 181 CPP).
            3. FUNDAMENTACIÓN: ¿Hay falta de logicidad o motivación en la sentencia?
            """
            perfil_sys = f"Sos un {nivel_penal} experto en casación y garantías procesales."

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

        # --- GENERADOR DE DOCUMENTOS ROBUSTOS ---
        st.subheader("📝 Generación de Piezas Procesales")
        
        if materia == "Cobro Judicial":
            if st.button("🛡️ Redactar Excepción de Prescripción y Caducidad"):
                with st.spinner("Redactando escrito de fondo..."):
                    prompt_doc = f"""
                    Redacta una EXCEPCIÓN DE PRESCRIPCIÓN Y CADUCIDAD de ALTO IMPACTO para los Juzgados de Cobro de Costa Rica.
                    ESTRUCTURA OBLIGATORIA:
                    - ENCABEZADO formal.
                    - HECHOS: Detalla las fechas encontradas en el análisis.
                    - FUNDAMENTOS: Cita el Código de Comercio (Art 968 y ss), Ley de Cobro Judicial y jurisprudencia de la Sala Primera.
                    - PETITORIA: Solicita el levantamiento de embargos y el archivo del expediente.
                    BASADO EN: {analisis_texto}
                    """
                    res_doc = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": prompt_doc}]
                    )
                    st.text_area("Borrador del Escrito:", value=res_doc.choices[0].message.content, height=600)
        
        else:
            if st.button(f"🚩 Redactar Recurso (Nivel {nivel_penal})"):
                with st.spinner("Redactando recurso de fondo..."):
                    prompt_doc = f"Redacta un RECURSO DE APELACIÓN O CASACIÓN técnico y contundente basado en estos agravios: {analisis_texto}. Cita el CPP de Costa Rica."
                    res_doc = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": prompt_doc}]
                    )
                    st.text_area("Borrador del Recurso:", value=res_doc.choices[0].message.content, height=600)

elif not api_key and archivo:
    st.warning("⚠️ Ingresa la API Key para activar el Radar.")
