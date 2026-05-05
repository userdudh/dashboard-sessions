import pandas as pd
from faker import Faker
import hashlib
from functools import lru_cache
from src.core.load import data_loader

#fake = Faker("pt_BR")

TARGET_TEST_USER = "user6442803380426375169" 
TARGET_TEST_COURSE = 10464
TEST_NAME_M1 = "Renan de Souza"
TEST_NAME_M2 = "Manuela Bezerra"

def preprocess(df):
    if df.empty:
        return df
    
    df = df.copy()
    df = df.sort_values(["username", "timecreated"], ignore_index=True)

    # users = df["username"].dropna().unique()
    # mapping = {}
    # used_names = set()
    # connectors = ["de", "da", "do", "dos", "das"]

    # for u in users:
    #     c_id = df[df["username"] == u]["courseid"].iloc[0] if "courseid" in df.columns else ""
        
    #     seed_string = f"{c_id}_{u}"
    #     base_seed = int(hashlib.md5(seed_string.encode()).hexdigest(), 16) % (2**32)
        
    #     for i in range(100):
    #         fake.seed_instance((base_seed + i) % (2**32))
    #         first, l1, l2 = fake.first_name(), fake.last_name(), fake.last_name()
    #         if l1 == l2: continue
    #         name = f"{first} {l1} {l2}" if (base_seed + i) % 2 == 0 else f"{first} {l1} {connectors[(base_seed + i) % len(connectors)]} {l2}"
    #         if name not in used_names:
    #             used_names.add(name)
    #             mapping[u] = name
    #             break

    # df["display_name"] = df["username"].map(mapping) 
    df["display_name"] = df["username"]
    
    return df

@lru_cache(maxsize=20)
def get_clean_data(courseid, method_number):
    df_raw = data_loader(courseid, method_number)
    return preprocess(df_raw)
