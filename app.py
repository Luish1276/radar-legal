# --- MOSTRAR RESULTADOS LIMPIOS ---
    if isinstance(res, dict):
        st.markdown(f"### ÚLTIMA GESTIÓN: `{res['ultima']}`")
        st.markdown(f"### MESES DE INACTIVIDAD: `{res['meses']}`")
        
        # Aquí es donde estaba el error, ahora está arreglado:
        if "🔴" in res['dictamen'] or "💀" in res['dictamen']:
            st.error(res['dictamen'])
        else:
            st.success(res['dictamen'])
    else:
        st.warning(res)