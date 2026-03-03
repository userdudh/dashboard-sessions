from src.core.load import data_loader
from src.core.preprocess import preprocess
import pandas as pd


def resumo_datas(df):
    if df.empty:
        print("DataFrame vazio.")
        return

    # garante datetime
    df["datetime"] = pd.to_datetime(df["datetime"])

    # 1️⃣ Primeiro log
    primeira_data = df["datetime"].min()

    # 2️⃣ Último log
    ultima_data = df["datetime"].max()

    # 3️⃣ Data com mais logs
    df["date"] = df["datetime"].dt.date

    contagem = df.groupby("date").size()
    data_mais_logs = contagem.idxmax()
    quantidade_max = contagem.max()

    print("\n===== RESUMO =====")
    print("Primeiro log:", primeira_data)
    print("Último log:", ultima_data)
    print("Data com mais logs:", data_mais_logs)
    print("Quantidade nessa data:", quantidade_max)


if __name__ == "__main__":
    df = data_loader()
    df = preprocess(df)

    resumo_datas(df)