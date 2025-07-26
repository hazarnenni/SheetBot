import streamlit as st
import requests
import json
import pandas as pd

from data_handler import df_to_serializable_dict
from gemini_client import configure_model, ask_gemini, clean_json
from charts import render_chart
from ui_components import show_history, add_to_history, download_report_button

SHEETDB_API = "https://sheetdb.io/api/v1/jidpqfmr9s32w"

st.title("📊 Gemini Google Sheets Chat Assistant")

configure_model(st.secrets["GEMINI_API_KEY"])

uploaded_file = st.file_uploader("Upload your Google Sheet CSV or Excel file", type=["csv", "xlsx"])
question = st.text_input("Ask something about your sheet:")

def get_data_from_sheetdb():
    res = requests.get(SHEETDB_API)
    return res.json()

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("### Uploaded Sheet Data Preview:")
    st.dataframe(df)

    csv = df.to_csv(index=False)

    sheet_data = df_to_serializable_dict(df)
else:
    sheet_data = get_data_from_sheetdb()
    csv = None

if question:
    gemini_response = ask_gemini(question, sheet_data)
    try:
        cleaned_response = clean_json(gemini_response)
        parsed = json.loads(cleaned_response)

        st.success("🧠 Gemini Answer:")
        st.write(parsed["answer"])

        add_to_history(question, parsed["answer"], parsed.get("chart"))

        if csv:
            download_report_button(parsed["answer"], csv)

        show_history()

        if "chart" in parsed:
            render_chart(parsed["chart"])

    except json.JSONDecodeError:
        st.warning("Gemini returned invalid JSON. Here's the raw response:")
        st.write(gemini_response)
