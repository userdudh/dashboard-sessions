import pandas as pd
from faker import Faker
import hashlib

fake = Faker("pt_BR")

def preprocess(df):
    if df.empty:
        return df
    
    df = df.copy()
    df = df.sort_values(["username", "timecreated"], ignore_index=True)

    users = df["username"].dropna().unique()
    mapping = {}
    used_names = set()
    connectors = ["de", "da", "do", "dos", "das"]

    for u in users:
        base_seed = int(hashlib.md5(str(u).encode()).hexdigest(), 16) % (2**32)
        for i in range(100):
            fake.seed_instance((base_seed + i) % (2**32))
            first, l1, l2 = fake.first_name(), fake.last_name(), fake.last_name()
            if l1 == l2: continue
            name = f"{first} {l1} {l2}" if (base_seed + i) % 2 == 0 else f"{first} {l1} {connectors[(base_seed + i) % len(connectors)]} {l2}"
            if name not in used_names:
                used_names.add(name)
                mapping[u] = name
                break

    df["display_name"] = df["username"].map(mapping)
    return df