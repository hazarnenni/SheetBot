import pandas as pd

def df_to_serializable_dict(df):
    df_copy = df.copy()
    for col in df_copy.select_dtypes(include=["datetime64", "datetimetz"]).columns:
        df_copy[col] = df_copy[col].astype(str)
    return df_copy.to_dict(orient="records")
