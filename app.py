import streamlit as st
import PyPDF2
import re
from datetime import datetime

st.set_page_config(page_title="Radar de Abandono Procesal", layout="wide")

def calcular_abandono(texto):
    # 1. Extraer todas las fechas del expediente (formato DD/MM/AAAA)
    fechas = re.findall(r'\d{2}/\d{2}/\d{4}', texto)
    
    if not fechas:
        return "No se encontraron fechas en el documento."

    # 2. Convertirlas a formato real y buscar la última
    lista_fechas = []
    for f in fechas:
        try:
            d = datetime.strptime(f, '%d/%m/%Y')
            if d.year > 2010 and d <= datetime.now():
                lista_fechas.append(d)
        except:
            continue
    
    if not lista_fechas:
        return "Sin movimientos recientes rastreables."

    ultima_gestion = max(lista_fechas)
    hoy = datetime.now()
    meses_inactivo = (hoy.year - ultima_gestion.year) * 12 + (hoy.month - ultima_gestion.month)

    # 3. VEREDICTO DE NEGLIGENCIA
    veredicto = ""
    if meses_inactivo >= 6:
        veredicto = f"🔴 ABANDONO DETECTADO: El abogado no mueve el caso hace {meses_inactivo} meses. ¡PROCEDE CADUCIDAD!"
    elif meses_inactivo >= 48:
        veredicto = f"💀 CASO MUERTO: {meses_inactivo} meses de inactividad. ¡PROCEDE PRESCRIPCIÓN!"
    else:
        veredicto = f"🟢 CASO ACTIVO: Último movimiento hace {meses_inactivo} meses."

    return {
        "ultima": ultima_gestion.strftime('%d/%m/%Y'),
        "meses": meses_inactivo,
        "dictamen": veredicto
    }

st.title("🕵️ Radar de Negligencia Legal")
st.write("Sube el PDF para saber si el abogado dejó morir el expediente.")

archivo = st.file_uploader("", type="pdf")

if archivo:
    lector = PyPDF2.PdfReader(archivo)
    texto_completo = "".join([p.extract_text() for p in lector.pages])
    
    res = calcular_abandono(texto_completo)
    
    if isinstance(res, dict):
        st.markdown(f"### ÚLTIMA GESTIÓN: `{res['ultima']}`")
        st.markdown(f"### MESES DE INACTIVIDAD: `{res['meses']}`")
        st.error(res['dictamen']) if "🔴" in res['dictamen'] or "💀" in res['dictamen'] else st.success(res['dictamen'])
    else:
        st.warning(res)