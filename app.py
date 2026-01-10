import streamlit as st
import pandas as pd
import os

# Configuración de la página
st.set_page_config(page_title="OBITER - Radar Legal", layout="wide")
st.title("🏛️ OBITER: Inteligencia de Auditoría Legal")
st.markdown("---")

# Intentar leer el archivo de datos
archivo = "OBITER.xlsx"

if os.path.exists(archivo):
    df = pd.read_excel(archivo)
    
    # --- INDICADORES RÁPIDOS ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Expedientes", len(df))
    
    # Verificar si existen columnas inteligentes
    if 'Estado_Procesal' in df.columns:
        riesgos = len(df[df['Estado_Procesal'].str.contains("🚩", na=False)])
        col2.metric("Alertas de Usura", riesgos)
    
    col3.info("Radar Actualizado")

    st.write("### 🔍 Análisis Detallado de Deudas")
    
    # --- TABLA INTELIGENTE ---
    st.dataframe(
        df, 
        column_config={
            "Ver_PDF": st.column_config.LinkColumn("Documento Original"),
            "Monto_Principal": "Monto Reclamado",
            "Tasa_Interes": "Tasa %",
            "Estado_Procesal": "Estatus"
        },
        use_container_width=True
    )

    # --- BOTÓN DE DESCARGA ---
    with open(archivo, "rb") as file:
        st.download_button(
            label="📥 Descargar Base de Datos Completa",
            data=file,
            file_name="Reporte_Radar_Legal.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.warning("⚠️ Esperando el archivo OBITER.xlsx. Ejecuta 'python main.py' en la terminal.")