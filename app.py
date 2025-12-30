import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="AI Risk Detection", layout="wide")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "risk_output.csv")

st.title("💳 AI-Based Transaction Risk Detection")

if not os.path.exists(CSV_PATH):
    st.error("❌ risk_output.csv not found. Run backend first (python main.py).")
    st.stop()

df = pd.read_csv(CSV_PATH)

st.success("✅ Risk output loaded successfully")
st.dataframe(df, use_container_width=True)
