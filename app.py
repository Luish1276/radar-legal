# --- MEJORA DE DETECCIÓN DE CESIÓN (Legitimación) ---
    terminos_cesion = [
        "cesión de derechos", "cesionario", "cedente", 
        "venta de cartera", "contrato de cesión", "endoso",
        "cesión de crédito", "traspaso de cartera", "fideicomiso de recuperación"
    ]
    
    # Buscamos si alguna de estas frases aparece en el texto (sin importar mayúsculas)
    es_cesion = "NO"
    for termino in terminos_cesion:
        if termino in texto.lower():
            es_cesion = f"SÍ (Detectado por término: '{termino}')"