import streamlit as st
import pandas as pd
import os

st.title("🏛️ OBITER: Radar Legal")

if os.path.exists("OBITER.xlsx"):
    df = pd.read_excel("OBITER.xlsx")
    st.dataframe(df)
else:
    st.warning("Esperando datos... Por favor, asegúrate de que OBITER.xlsx esté listo.")