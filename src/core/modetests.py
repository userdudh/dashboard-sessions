import pandas as pd
from src.core.load import data_loader
from src.core.preprocess import preprocess

def get_test_mode_data(course_id, target_username, nome_ficticio_1="Usuário - Método 1", nome_ficticio_2="Usuário - Método 2"):

    df_m1_raw = data_loader(course_id, method_number=1)
    df_m1 = preprocess(df_m1_raw)
    df_m1 = df_m1[df_m1['username'] == target_username].copy()
    df_m1['display_name'] = nome_ficticio_1
    df_m1['metodo'] = 1

    df_m2_raw = data_loader(course_id, method_number=2)
    df_m2 = preprocess(df_m2_raw)
    df_m2 = df_m2[df_m2['username'] == target_username].copy()
    df_m2['display_name'] = nome_ficticio_2 
    df_m2['metodo'] = 2

    df_test_mode = pd.concat([df_m1, df_m2], ignore_index=True)
    
    return df_test_mode