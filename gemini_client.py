import json
import re
import google.generativeai as genai

genai.configure(api_key=None)

model = None

def configure_model(api_key, model_name="models/gemini-1.5-flash"):
    global model
    genai.configure(api_key=api_key)
    global model
    model = genai.GenerativeModel(model_name)

def clean_json(json_string):
    json_string = re.sub(r'```json\s*([\s\S]*?)\s*```', r'\1', json_string, flags=re.MULTILINE)
    json_string = re.sub(r'//.*?\n', '\n', json_string)
    json_string = re.sub(r',(\s*[}\]])', r'\1', json_string)
    json_string = json_string.strip()
    if json_string.startswith('"') and json_string.endswith('"'):
        json_string = json_string[1:-1]
    json_string = json_string.replace('\\"', '"')
    return json_string

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
