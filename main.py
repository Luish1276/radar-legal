st.set_page_config(page_title="Radar Legal CR", layout="wide", page_icon="⚖️")

# Estilo personalizado para mejorar la visibilidad
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    </style>
    """, unsafe_markdown=True)

st.title("⚖️ Radar Legal Avanzado - Costa Rica")
st.markdown("---")

# --- LÓGICA DE BÚSQUEDA ---
def buscar_en_archivo(contenido_pdf, palabras_clave):
    try:
        with pdfplumber.open(BytesIO(contenido_pdf)) as pdf:
            resultados = []
            for i, pagina in enumerate(pdf.pages):
                texto = pagina.extract_text()
                if texto:
                    for palabra in palabras_clave:
                        if palabra and palabra.lower() in texto.lower():
                            inicio = max(0, texto.lower().find(palabra.lower()) - 100)
                            fin = inicio + 250
                            contexto = "..." + texto[inicio:fin] + "..."
                            resultados.append({
                                "Página": i + 1,
                                "Categoría/Palabra": palabra,
                                "Extracto": contexto.replace("\n", " ")
                            })
            return pd.DataFrame(resultados), None
    except Exception as e:
        return None, f"Error al procesar el PDF: {str(e)}"

# --- BARRA LATERAL (CALENDARIO) ---
st.sidebar.header("📅 Configuración de Fecha")
fecha_consulta = st.sidebar.date_input("Seleccione fecha del Boletín:", datetime.now())
fecha_str = fecha_consulta.strftime("%d/%m/%Y")

dia, mes, anio = fecha_consulta.strftime("%d"), fecha_consulta.strftime("%m"), fecha_consulta.strftime("%Y")
url_boletin = f"https://www.imprentanacional.go.cr/boletin/?date={dia}/{mes}/{anio}"

st.sidebar.markdown(f"**Consultando:** {fecha_str}")
st.sidebar.info("Para fechas antiguas, asegúrese de que la fecha seleccionada sea un día hábil.")

# --- CUERPO PRINCIPAL: PESTAÑAS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏛️ Remates", 
    "🚗 Lesiones", 
    "⚖️ Prescripciones", 
    "🔍 Consulta Cliente", 
    "📂 Analizar PDF Propio"
])

# Función auxiliar para descargar y buscar
def ejecutar_busqueda_url(lista_palabras):
    with st.spinner("Conectando con la Imprenta Nacional..."):
        try:
            response = requests.get(url_boletin, timeout=15)
            if response.status_code != 200 or b'%PDF' not in response.content[:100]:
                st.info("No hay un boletín oficial disponible para esta fecha (Feriado, fin de semana o no cargado).")
                return
            
            df, error = buscar_en_archivo(response.content, lista_palabras)
            if error: st.error(error)
            elif not df.empty:
                st.success(f"¡Se encontraron {len(df)} coincidencias!")
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No se encontraron resultados para los criterios seleccionados.")
        except:
            st.error("Error de conexión. Intente con otra fecha o suba el archivo manualmente.")

with tab1:
    st.subheader("Búsqueda de Remates")
    if st.button("Ejecutar Escaneo de Remates"):
        ejecutar_busqueda_url(["Remate", "Primer remate", "Segunda publicación"])

with tab2:
    st.subheader("Casos de Lesiones Culposas")
    if st.button("Buscar Expedientes de Tránsito"):
        ejecutar_busqueda_url(["Lesiones culposas", "Accidente de tránsito", "Tránsito"])

with tab3:
    st.subheader("Edictos de Prescripción")
    if st.button("Buscar Prescripciones"):
        ejecutar_busqueda_url(["Prescripción", "Interrupción de prescripción"])

with tab4:
    st.subheader("🔍 Localizador de Clientes")
    dato_cliente = st.text_input("Ingrese Cédula o Nombre completo del cliente:")
    if st.button("Rastrear Cliente en esta Fecha"):
        if dato_cliente:
            ejecutar_busqueda_url([dato_cliente])
        else:
            st.error("Por favor, ingrese un dato para buscar.")

with tab5:
    st.subheader("📂 Analizador de Archivos PDF Locales")
    st.markdown("Suba cualquier PDF (Boletines viejos, Gacetas o expedientes) para buscar palabras clave.")
    
    archivo_subido = st.file_uploader("Arrastre su archivo aquí", type="pdf")
    palabras_extra = st.text_input("Palabras adicionales a buscar (separadas por coma):", "Remate, Cédula, Nombre")
    
    if archivo_subido and st.button("Analizar PDF Subido"):
        with st.spinner("Procesando archivo local..."):
            lista_custom = [p.strip() for p in palabras_extra.split(",")]
            df, error = buscar_en_archivo(archivo_subido.read(), lista_custom)
            if error: st.error(error)
            elif not df.empty:
                st.success("Resultados encontrados en el archivo subido:")
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No se encontraron las palabras clave en el documento subido.")
