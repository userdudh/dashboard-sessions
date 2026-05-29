import pandas as pd
from functools import lru_cache
from src.core.load import data_loader

def preprocess(df):
    if df.empty:
        return df
    
    df = df.copy()
    df = df.sort_values(["username", "timecreated"], ignore_index=True)
    df["display_name"] = df["username"]
    
    return df

@lru_cache(maxsize=20)
def get_clean_data(courseid, method_number):
    df_raw = data_loader(courseid, method_number)
    return preprocess(df_raw)
