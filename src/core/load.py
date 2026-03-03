import pandas as pd
from pathlib import Path

def data_loader(method_number=1):
    filename = f"teaching-with-moodle_STT {method_number}.csv"
    relative_path = Path(__file__).parent.parent.parent / "data" / filename

    if not relative_path.exists():
        print(f"Arquivo não encontrado em {relative_path}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(relative_path)
        return df
    except Exception as e:
        print(f"Erro ao ler o CSV {filename}: {e}")
        return pd.DataFrame()