import streamlit as st
import json

def show_history():
    if "history" not in st.session_state:
        st.session_state.history = []

    st.markdown("### 🕑 Question & Answer History")

    for i, entry in enumerate(st.session_state.history[::-1], 1):
        st.markdown(f"**Q{i}:** {entry['question']}")
        st.markdown(f"**A{i}:** {entry['answer']}")
        if "chart" in entry:
            st.write("📊 Chart included")

def add_to_history(question, answer, chart=None):
    if "history" not in st.session_state:
        st.session_state.history = []

    entry = {"question": question, "answer": answer}
    if chart:
        entry["chart"] = chart
    st.session_state.history.append(entry)

def download_report_button(answer_text, csv_data):
    st.download_button(
        label="Download answer report as TXT",
        data=answer_text,
        file_name="gemini_answer.txt",
        mime="text/plain",
    )
    st.download_button(
        label="Download current sheet data as CSV",
        data=csv_data,
        file_name="sheet.csv",
        mime="text/csv",
    )
