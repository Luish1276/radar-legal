import streamlit as st
import pandas as pd
import PyPDF2
import re
import io

st.set_page_config(page_title="OBITER - Auditoría Legal Pro", layout="wide")

st.title("🏛️ OBITER: Inteligencia Legal Estratégica")
st.markdown("### Auditoría de Expedientes (Análisis de Viabilidad)")

def analizar_pro(texto):
    # --- EXTRACCIÓN DE DATOS CLAVE ---
    monto = re.search(r'¢\s?([\d\.]+,\d{2})', texto)
    exp = re.search(r'\d{2}-\d{6}-\d{4}-[A-Z0-9]+', texto)
    tasa = re.search(r'(\d+,\d+)%\s+mensual', texto)
    
    # --- LÓGICA DE AUDITORÍA (Lo que importa) ---
    # 1. Análisis de Título Ejecutivo
    tiene_certificacion = "SÍ" if "certificación" in texto.lower() else "NO DETECTADA"
    
    # 2. Análisis de Prescripción (Basado en fechas encontradas)
    fechas = re.findall(r'\d{2}/\d{2}/\d{4}', texto)
    prescripcion = "REVISAR (Fechas antiguas)" if len(fechas) > 0 else "Al día"

    # 3. Hallazgo de Cláusulas / Abuso
    hallazgo = "Estándar"
    if "seguro" in texto.lower() or "comisión" in texto.lower():
        hallazgo = "Posible Cláusula Abusiva"
    
    tasa_val = tasa.group(1) if tasa else "0"
    
    return {
        "Expediente": exp.group(0) if exp else "S/N",
        "Monto": f"¢{monto.group(1)}" if monto else "S/D",
        "Título Válido": tiene_certificacion,
        "Riesgo Prescripción": prescripcion,
        "Hallazgo Técnico": hallazgo,
        "Acción Recomendada": "Interponer Excepción" if "🚩" in hallazgo or "REVISAR" in prescripcion else "Negociar Arreglo"
    }

# --- INTERFAZ ---
uploaded_files = st.file_uploader("Suba expedientes para auditoría rápida", type="pdf", accept_multiple_files=True)

if uploaded_files:
    data = []
    for f in uploaded_files:
        reader = PyPDF2.PdfReader(f)
        full_text = "".join([p.extract_text() for p in reader.pages])
        res = analizar_pro(full_text)
        res["Nombre Archivo"] = f.name
        data.append(res)
    
    df = pd.DataFrame(data)
    st.write("---")
    st.subheader("📋 Matriz de Estrategia Legal")
    st.dataframe(df, use_container_width=True)
    
    # Exportar para el cliente
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    st.download_button("📥 Descargar Informe para Cliente/Jefe", buf.getvalue(), "Auditoria_Legal.xlsx")