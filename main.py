import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Radar Padrón: Prospección", layout="wide", page_icon="🚀")

# --- ESTILO ---
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .main { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Radar Padrón: Inteligencia de Prospección")
st.subheader("Buscador de Demandas Nuevas (Antes de Notificación)")

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["📊 Panel de Prospección", "📥 Carga de Padrón", "🤖 Estado del Robot"])

with tab1:
    st.write("### Lista de Clientes Potenciales Detectados")
    st.info("Estos expedientes han sido cruzados con el Padrón y detectados como 'Sin Notificar'.")
    
    # Simulación de la base de datos que llenará el robot
    data_prospeccion = [
        {"Cédula": "1-0988-0234", "Nombre": "JUAN PEREZ SOLANO", "Expediente": "26-000124-1205-CJ", "Acreedor": "BANCO NACIONAL", "Monto Est.": "₡2.500.000", "Estado": "ADMITIDA"},
        {"Cédula": "2-0455-0876", "Nombre": "MARIA RUIZ FONSECA", "Expediente": "26-000567-1158-CJ", "Acreedor": "INSTACREDIT", "Monto Est.": "₡850.000", "Estado": "PENDIENTE NOTIFICAR"}
    ]
    
    df = pd.DataFrame(data_prospeccion)
    st.dataframe(df, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("📞 Marcar como Llamado")
    with col2:
        st.download_button("📥 Descargar Reporte para Ventas", df.to_csv(index=False), "prospeccion_hoy.csv")

with tab2:
    st.header("Carga de Cédulas del Padrón")
    st.write("Sube el segmento del padrón electoral que deseas monitorear.")
    archivo_padron = st.file_uploader("Archivo Padrón (Excel/CSV):", type=["csv", "xlsx"])
    
    if archivo_padron:
        st.success("✅ Padrón cargado. El robot iniciará el barrido secuencial.")
        # Aquí procesamos el archivo para extraer solo las cédulas
        # df_padron = pd.read_csv(archivo_padron)

with tab3:
    st.header("Control del Robot de Búsqueda")
    st.write("Estado de la conexión con Gestión en Línea:")
    
    st.status("Conectado a Servidores Judiciales", state="running")
    st.progress(35, text="Escaneando cédulas... 350/1000")
    
    st.markdown("""
    **Parámetros de Búsqueda:**
    * **Frecuencia:** Cada 24 horas.
    * **Filtro:** Solo procesos de COBRO JUDICIAL.
    * **Jurisdicción:** Todo el país.
    """)
