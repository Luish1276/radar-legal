import os
import PyPDF2
import re
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN OBITER ---
BASE_DATOS_OBITER = "OBITER.xlsx"
CARPETA_EXPEDIENTES = CARPETA_EXPEDIENTES = "."
ARCHIVO_EXCEPCIONES = "REVISION_MANUAL.txt"

def motor_radar_punteria_total():
    # 1. Cargar OBITER existente
    if os.path.exists(BASE_DATOS_OBITER):
        df_obiter = pd.read_excel(BASE_DATOS_OBITER)
    else:
        df_obiter = pd.DataFrame(columns=["Fecha_Analisis", "Expediente", "Cedula", "Estado_Procesal", "Calidad_ID"])

    if not os.path.exists(CARPETA_EXPEDIENTES):
        print(f"❌ Carpeta '{CARPETA_EXPEDIENTES}' no encontrada.")
        return

    archivos = [f for f in os.listdir(CARPETA_EXPEDIENTES) if f.endswith('.pdf')]
    excepciones = []

    print(f"🚀 Analizando {len(archivos)} archivos. Generando OBITER y Filtro de Excepciones...")

    for archivo in archivos:
        try:
            ruta = os.path.join(CARPETA_EXPEDIENTES, archivo)
            with open(ruta, 'rb') as f:
                lector = PyPDF2.PdfReader(f)
                texto_busqueda = ""
                for i in range(min(7, len(lector.pages))):
                    texto_busqueda += lector.pages[i].extract_text().upper() + "\n"

                # --- SENSOR DE IDENTIDAD ---
                cedula = None
                calidad = "ALTA"
                m1 = re.search(r"(\d-\d{3,4}-\d{4}|\d-\d{3}-\d{6})", texto_busqueda)
                m2 = re.search(r"(?<!-)(\b\d{9,10}\b)(?!-)", texto_busqueda)
                
                if m1:
                    cedula = m1.group(1)
                elif m2:
                    cedula = m2.group(1)
                    calidad = "MEDIA (PEGADA)"
                else:
                    cedula = "SIN_ID_MANUAL"
                    calidad = "NULA"
                    excepciones.append(archivo) # Guardamos el nombre para el reporte de fallos

                # --- SENSOR DE EXPEDIENTE ---
                exp_m = re.search(r"(\d{2}-\d{6}-\d{4}-[A-Z]{2})", texto_busqueda)
                expediente = exp_m.group(1) if exp_m else archivo.replace(".pdf", "")

                # --- LÓGICA DE AUDITORÍA ---
                es_critico = "EMBARGO" in texto_busqueda and "SOLICITO" not in texto_busqueda[-1200:]
                
                # --- ACTUALIZACIÓN DE OBITER ---
                if expediente in df_obiter['Expediente'].values:
                    idx = df_obiter[df_obiter['Expediente'] == expediente].index[0]
                    if df_obiter.at[idx, 'Cedula'] == "SIN_ID_MANUAL" and cedula != "SIN_ID_MANUAL":
                        df_obiter.at[idx, 'Cedula'] = cedula
                        df_obiter.at[idx, 'Calidad_ID'] = calidad
                else:
                    nuevo = {
                        "Fecha_Analisis": datetime.now().strftime("%Y-%m-%d"),
                        "Expediente": expediente,
                        "Cedula": cedula,
                        "Estado_Procesal": "🚩 CRÍTICO" if es_critico else "✅ ACTIVO",
                        "Calidad_ID": calidad
                    }
                    df_obiter = pd.concat([df_obiter, pd.DataFrame([nuevo])], ignore_index=True)

        except Exception as e:
            print(f"❌ Error en {archivo}: {e}")

    # 2. Guardar el Activo Principal (Excel)
    df_obiter.to_excel(BASE_DATOS_OBITER, index=False)

    # 3. Guardar el Filtro de Excepciones (Txt)
    with open(ARCHIVO_EXCEPCIONES, "w", encoding="utf-8") as f_exc:
        f_exc.write(f"--- REVISIÓN MANUAL REQUERIDA ({datetime.now().strftime('%Y-%m-%d')}) ---\n")
        f_exc.write(f"Los siguientes {len(excepciones)} archivos no pudieron ser identificados automáticamente:\n\n")
        for ex in excepciones:
            f_exc.write(f"- {ex}\n")

    print(f"\n✅ Sincronización completa.")
    print(f"📁 Base de Datos: {BASE_DATOS_OBITER}")
    print(f"⚠️  Casos para revisar a mano: {len(excepciones)} (Ver {ARCHIVO_EXCEPCIONES})")

if __name__ == "__main__":
    motor_radar_punteria_total()