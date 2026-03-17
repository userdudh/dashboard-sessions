import pandas as pd
import json
from pathlib import Path

def data_loader(method_number=1):
    filename = f"teaching-with-moodle_STT {method_number}.json"
    relative_path = Path(__file__).parent.parent.parent / "data" / filename

    if not relative_path.exists():
        print(f"Arquivo não encontrado em {relative_path}")
        return pd.DataFrame()

    try:
        with open(relative_path, 'r', encoding='utf-8') as f:
            raw_json = json.load(f)
            
        flat_data = []
        for course in raw_json:
            courseid = course.get("courseid")
            
            for user in course.get("users", []):
                username = user.get("username")
                
                for session in user.get("user_sessions", []):
                    sessao_id = session.get("sessao_id")
                    
                    for event in session.get("events", []):
                        flat_data.append({
                            "courseid": courseid,
                            "username": username,
                            "sessao_id": sessao_id,
                            "eventname": event.get("eventname"),
                            "class": event.get("class"),
                            "timecreated": event.get("timecreated"),
                            "datetime": event.get("timecreated") 
                        })
        

        df = pd.DataFrame(flat_data)
        

        if not df.empty and "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"], unit='s')
            
        return df

    except Exception as e:
        print(f"Erro ao processar o arquivo JSON {filename}: {e}")
        return pd.DataFrame()