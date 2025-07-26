import streamlit as st
import google.generativeai as genai
import requests
import json
import pandas as pd
import re

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("models/gemini-1.5-flash")

SHEETDB_API = "https://sheetdb.io/api/v1/jidpqfmr9s32w"

st.title("📊 Gemini Google Sheets Chat Assistant")

uploaded_file = st.file_uploader("Upload your Google Sheet CSV or Excel file", type=["csv", "xlsx"])
question = st.text_input("Ask something about your sheet:")

def get_data_from_sheetdb():
    res = requests.get(SHEETDB_API)
    return res.json()

def clean_json(json_string):
    json_string = re.sub(r'```json\s*([\s\S]*?)\s*```', r'\1', json_string, flags=re.MULTILINE)
    json_string = re.sub(r'//.*?\n', '\n', json_string)
    json_string = re.sub(r',(\s*[}\]])', r'\1', json_string)
    json_string = json_string.strip()
    if json_string.startswith('"') and json_string.endswith('"'):
        json_string = json_string[1:-1]
    json_string = json_string.replace('\\"', '"')
    return json_string

def df_to_serializable_dict(df):
    df_copy = df.copy()
    for col in df_copy.select_dtypes(include=["datetime64", "datetimetz"]).columns:
        df_copy[col] = df_copy[col].astype(str)
    return df_copy.to_dict(orient="records")

def ask_gemini(question, sheet_data):
    prompt = f"""
You are a smart data assistant. Interpret the following sheet data and user question.

DATA:
{json.dumps(sheet_data)}

QUESTION:
{question}

If possible, return a JSON object like:
{{
  "answer": "Short text explanation here.",
  "chart": {{
    "type": "bar",
    "x": ["Product A", "Product B"],
    "y": [100, 150]
  }}
}}

If a chart is not applicable, just return:
{{
  "answer": "Textual response only."
}}

Only return valid JSON. Do not include markdown or explanation.
"""
    response = model.generate_content(prompt)
    return response.text

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("### Uploaded Sheet Data Preview:")
    st.dataframe(df)

    csv = df.to_csv(index=False)
    st.download_button("Download current sheet data as CSV", csv, "sheet.csv")

    sheet_data = df_to_serializable_dict(df)

else:
    sheet_data = get_data_from_sheetdb()

if question:
    gemini_response = ask_gemini(question, sheet_data)

    try:
        cleaned_response = clean_json(gemini_response)
        parsed = json.loads(cleaned_response)

        st.success("🧠 Gemini Answer:")
        st.write(parsed["answer"])

        if "chart" in parsed:
            chart = parsed["chart"]

            df_chart = pd.DataFrame({
                "x": chart["x"],
                "y": chart["y"]
            }).set_index("x")

            if chart["type"] == "bar":
                st.bar_chart(df_chart)
            elif chart["type"] == "line":
                st.line_chart(df_chart)
            elif chart["type"] == "pie":
                st.write("Pie chart not natively supported by Streamlit, showing bar chart instead:")
                st.bar_chart(df_chart)

    except json.JSONDecodeError:
        st.warning("Gemini returned invalid JSON. Here's the raw response:")
        st.write(gemini_response)
