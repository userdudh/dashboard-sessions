import pandas as pd

def _aggregate_sessions(df):

    if df.empty:
        return pd.DataFrame()
    
    dataframe = (
        df.groupby(["username", "sessao_id"], as_index=False)
          .agg(
              inicio=("datetime", "min"),
              fim=("datetime", "max"),
              eventos=("datetime", "count")
          )
    )
    return dataframe

def method_1(df): return _aggregate_sessions(df)
def method_2(df): return _aggregate_sessions(df)