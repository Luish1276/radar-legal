import streamlit as st
import PyPDF2
import re
from datetime import datetime

st.set_page_config(page_title="Radar de Negligencia OBITER", layout="wide")

def analizar_negligencia(texto):
    # 1. Extraer fechas
    fechas = re.findall(r'\d{2}/\d{2}/\d{4}', texto)
    if not fechas:
        return "No se detectan fechas de gestión."

    lista_fechas = []
    for f in fechas:
        try:
            d = datetime.strptime(f, '%d/%m/%Y')
            if 2010 < d.year <= datetime.now().year:
                lista_fechas.append(d)
        except:
            continue
    
    if not lista_fechas:
        return "Sin historial de fechas válido."

    ultima_gestion = max(lista_fechas)
    hoy = datetime.now()
    meses_inactivo = (hoy.year - ultima_gestion.year) * 12 + (hoy.month - ultima_gestion.month)

    # 2. Rastrear palabras clave de notificación
    tiene_notificacion_reciente = any(palabra in texto.lower() for palabra in ["notificado", "acta de notificación", "cedula de notificación"])
    
    # 3. Dictamen de Negligencia
    alertas = []
    
    if meses_inactivo >= 6:
        alertas.append(f"🔴 ABANDONO PROCESAL: {meses_inactivo} meses sin movimiento. ¡Procede Caducidad de Instancia!")
    elif meses_inactivo >= 3 and not tiene_notificacion_reciente:
        alertas.append(f"⚠️ NEGLIGENCIA DE GESTIÓN: {meses_inactivo} meses sin rastro de notificación exitosa. El abogado no está localizando al deudor.")
    elif meses_inactivo < 3:
        alertas.append(f"🟢 CASO ACTIVO: Última gestión hace {meses_inactivo} meses.")

    return {
        "ultima": ultima_gestion.strftime('%d/%m/%Y'),
        "meses": meses_inactivo,
        "alertas": alertas
    }

# --- INTERFAZ LIMPIA ---
st.title("🕵️ Radar de Negligencia Legal")
st.write("Detección automática de abandono y falta de notificación.")

archivo = st.file_uploader("Suba el PDF del expediente", type="pdf")

if archivo:
    lector = PyPDF2.PdfReader(archivo)
    texto_completo = "".join([p.extract_text() for p in lector.pages])
    
    res = analizar_negligencia(texto_completo)
    
    if isinstance(res, dict):
        st.markdown(f"### ÚLTIMA GESTIÓN: `{res['ultima']}`")
        st.markdown(f"### MESES DE INACTIVIDAD: `{res['meses']}`")
        
        for mensaje in res['alertas']:
            if "🔴" in mensaje:
                st.error(mensaje)
            elif "⚠️" in mensaje:
                st.warning(mensaje)
            else:
                st.success(mensaje)
    else:
        st.info(res)