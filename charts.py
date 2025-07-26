import streamlit as st
import pandas as pd

def render_chart(chart):
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
