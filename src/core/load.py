import pandas as pd
import json
from pathlib import Path


def data_loader(courseid, method_number=1):
    filename = f"metodo{method_number}-curso{courseid}.json"
    relative_path = Path(__file__).parent.parent.parent / "data" / filename

    if not relative_path.exists():
        print(f"Arquivo não encontrado em {relative_path}")
        return pd.DataFrame()

    try:
        with open(relative_path, "r", encoding="utf-8") as f:
            dados = json.load(f)

        # O seu JSON vem assim: [ { courseid, users } ]
        # Então precisamos pegar o primeiro item da lista.
        if isinstance(dados, list):
            if not dados:
                return pd.DataFrame()
            course = dados[0]
        else:
            course = dados

        flat_data = []
        course_id = course.get("courseid")

        for user in course.get("users", []):
            username = user.get("userid")

            for session in user.get("user_sessions", []):
                sessao_id = session.get("sessao_id")

                for event in session.get("events", []):
                    flat_data.append({
                        "courseid": course_id,
                        "username": username,
                        "sessao_id": sessao_id,
                        "class": event.get("class"),
                        "timecreated": event.get("t"),
                        "datetime": event.get("t"),
                    })

        df = pd.DataFrame(flat_data)

        if not df.empty and "datetime" in df.columns:
            df["datetime"] = (
                pd.to_datetime(df["datetime"], unit="s", utc=True, errors="coerce")
                .dt.tz_convert("America/Recife")
                .dt.tz_localize(None)
            )

        return df

    except Exception as e:
        print(f"Erro ao processar o arquivo {filename}: {e}")
        return pd.DataFrame()