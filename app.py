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
    
    # Esta opción separa los programas para que no se confundan
    materia = st.radio("Seleccione el Módulo:", ["Cobro Judicial", "Radar Penal"])
    
    st.divider()
    st.info(f"Módulo Activo: {materia}")
    if materia == "Cobro Judicial":
        st.write("🔍 Buscando: Prescripción, Caducidad y Títulos.")
    else:
        st.write("🔍 Buscando: Nulidades Art. 178/181 y Vicios de Prueba.")

# 3. CARGA DE EXPEDIENTE
archivo = st.file_uploader(f"Subir documento para {materia} (PDF)", type=["pdf"])

if archivo and api_key:
    with st.spinner(f"Ejecutando motor de {materia}..."):
        # Extracción de texto
        texto_completo = ""
        with pdfplumber.open(archivo) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t: texto_completo += t + "\n"
        
        client = openai.OpenAI(api_key=api_key)

        # --- SEPARACIÓN LÓGICA DE PROGRAMAS ---
        if materia == "Cobro Judicial":
            # MÓDULO COBRO: Especialista en Derecho Mercantil y Procesal Civil
            prompt_instruccion = """
            Sos un experto en COBRO JUDICIAL de Costa Rica. Analizá este documento:
            1. PRESCRIPCIÓN: Revisá fechas de vencimiento y última actuación. Determiná si ya operó la prescripción (4 años Mercantil o plazos específicos).
            2. CADUCIDAD: Revisá si hay inactividad procesal suficiente para alegar caducidad del proceso.
            3. TÍTULO EJECUTIVO: ¿Es un pagaré, letra o factura? ¿Cumple los requisitos de ley?
            4. DOCUMENTO REQUERIDO: Identificá si se debe redactar una Excepción de Prescripción o una Contestación.
            """
        else:
            # MÓDULO RADAR PENAL: Especialista en Garantías Procesales
            prompt_instruccion = """
            Sos un experto en DERECHO PENAL de Costa Rica. Analizá este caso:
            1. NULIDADES: Buscá violaciones específicas al Art. 178 del CPP.
            2. VICIOS DE PRUEBA: Identificá prueba espuria o ilegal según el Art. 181 del CPP.
            3. TIPICIDAD: ¿La conducta encaja exactamente en el Código Penal?
            4. DOCUMENTO REQUERIDO: Identificá si procede un Recurso de Apelación o un Incidente de Nulidad.
            """

        # EJECUCIÓN DEL ANÁLISIS DE ALTO IMPACTO
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"IA Jurídica de Alto Impacto (CR). Módulo: {materia}. Prohibido mezclar conceptos de otras materias."},
                {"role": "user", "content": f"{prompt_instruccion}\n\nTEXTO DEL EXPEDIENTE:\n{texto_completo[:16000]}"}
            ],
            temperature=0.1 # Máxima precisión
        )

        analisis_final = response.choices[0].message.content
        st.subheader(f"📊 Dictamen Especializado: {materia}")
        st.markdown(analisis_final)

        st.divider()

        # 4. GENERACIÓN DE DOCUMENTOS RESPECTIVOS
        st.subheader("📝 Generación de Escritos Legales")
        
        if materia == "Cobro Judicial":
            btn_label = "🛡️ Crear Excepción de Prescripción y Caducidad"
            doc_type = "Excepción de Prescripción y Caducidad formal para Cobro Judicial"
        else:
            btn_label = "🚩 Crear Recurso de Apelación / Incidente"
            doc_type = "Recurso de Apelación o Incidente de Nulidad basado en vicios procesales"

        if st.button(btn_label):
            with st.spinner("Redactando documento de alto impacto..."):
                res_doc = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Abogado litigante senior de Costa Rica. Redacción técnica y formal."},
                        {"role": "user", "content": f"Redactá el documento '{doc_type}' basado en este análisis: {analisis_final}. Usá el formato oficial de los tribunales de CR."}
                    ]
                )
                st.success("✅ Documento redactado con éxito.")
                st.text_area("Borrador para copiar y pegar:", value=res_doc.choices[0].message.content, height=500)

elif not api_key and archivo:
