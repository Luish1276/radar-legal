# ... (Mantenemos las importaciones de arriba) ...

# Solo hay que añadir esta lógica en la sección de pestañas:
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏛️ Remates", "🚗 Lesiones", "⚖️ Prescripciones", "🔍 Consulta Cliente", "📂 Subir Archivo"])

# ... (Las pestañas 1 a 4 se quedan igual) ...

with tab5:
    st.header("Analizar PDF Externo")
    st.info("Suba un Boletín o Gaceta que tenga guardado en su computadora para buscar palabras clave o cédulas.")
    
    archivo_subido = st.file_uploader("Arrastre aquí su archivo PDF", type="pdf")
    
    if archivo_subido is not None:
        if st.button("Analizar Archivo Subido"):
            with st.spinner("Escaneando su documento..."):
                with pdfplumber.open(BytesIO(archivo_subido.read())) as pdf:
                    # Aquí buscamos TODO: Remates, Lesiones y el nombre que pusiste en la pestaña 4
                    palabras_propias = ["Remate", "Lesiones culposas", "Prescripción", dato_cliente]
                    resultados = []
                    for i, pagina in enumerate(pdf.pages):
                        texto = pagina.extract_text()
                        if texto:
                            for palabra in palabras_propias:
                                if palabra and palabra.lower() in texto.lower():
                                    resultados.append({"Página": i+1, "Encontrado": palabra})
                    
                    if resultados:
                        st.success("¡Análisis completado!")
                        st.table(pd.DataFrame(resultados))
                    else:
                        st.warning("No se encontraron las palabras clave en este documento.")
