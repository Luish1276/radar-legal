import streamlit as st
import pandas as pd
import PyPDF2
import re
import io

st.set_page_config(page_title="OBITER - Radar Legal Privado", layout="wide")

st.title("🏛️ OBITER: Procesamiento Privado de Expedientes")
st.write("Suba sus archivos PDF aquí. El análisis se hace en tiempo real y no se guarda en ningún servidor externo.")

# --- FUNCIÓN CEREBRO (Extraída de tu main.py) ---
def analizar_texto(texto):
    monto_search = re.search(r'¢\s?([\d\.]+,\d{2})', texto)
    interes_search = re.search(r'(\d+,\d+)%\s+mensual', texto)
    expediente_search = re.search(r'\d{2}-\d{6}-\d{4}-[A-Z0-9]+', texto)
    
    monto = monto_search.group(1) if monto_search else "No detectado"
    interes = interes_search.group(1) if interes_search else "0"
    
    # Lógica de Usura
    try:
        tasa_num = float(interes.replace(',', '.'))
        estado = "🚩 REVISAR USURA" if tasa_num > 3.0 else "✅ ESTÁNDAR"
    except:
        estado = "Análisis manual requerido"

    return {
        "Expediente": expediente_search.group(0) if expediente_search else "S/N",
        "Monto_Principal": monto,
        "Tasa_Interes": f"{interes}%",
        "Estado_Procesal": estado
    }

# --- INTERFAZ DE CARGA ---
archivos_subidos = st.file_uploader("Seleccione uno o varios PDFs", type="pdf", accept_multiple_files=True)

if archivos_subidos:
    resultados = []
    
    for archivo_pdf in archivos_subidos:
        # Leer el PDF directamente desde la web
        lector = PyPDF2.PdfReader(archivo_pdf)
        texto_completo = ""
        for pagina in lector.pages:
            texto_completo += pagina.extract_text()
        
        # Analizar
        datos = analizar_texto(texto_completo)
        datos["Nombre_Archivo"] = archivo_pdf.name
        resultados.append(datos)
    
    # Mostrar resultados
    df = pd.DataFrame(resultados)
    
    st.write("---")
    st.subheader("📊 Resultados del Análisis")
    st.dataframe(df, use_container_width=True)
    
    # Botón para descargar el Excel resultante
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 Descargar Reporte en Excel",
        data=buffer.getvalue(),
        file_name="analisis_obiter.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )