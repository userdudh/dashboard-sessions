import pandas as pd
from dash import Input, Output
from src.core.session_methods import method_1, method_2
from src.core.preprocess import get_clean_data, TARGET_TEST_USER, TARGET_TEST_COURSE, TEST_NAME_M1, TEST_NAME_M2
from src.ui.components.charts import fig_week_bars

METHODS = {"m1": method_1, "m2": method_2}

def register_charts_callbacks(app, _): 
    
    @app.callback(
        Output("sessions-store", "data"),
        [Input("filters-store", "data"),
         Input("app-mode-switch", "value")],
    )
    def compute_sessions(filters, mode):

        if mode == "test":
            start = filters.get("start") if filters else None
            end = filters.get("end") if filters else None
            users = filters.get("users", []) if filters else []
            
            df_m1_raw = get_clean_data(TARGET_TEST_COURSE, 1)
            df_m1 = df_m1_raw[df_m1_raw["username"] == TARGET_TEST_USER].copy()
            sess_m1 = method_1(df_m1) if not df_m1.empty else pd.DataFrame()
            
            if not sess_m1.empty:
                sess_m1["username"] = "test_m1"
                sess_m1["display_name"] = TEST_NAME_M1

            df_m2_raw = get_clean_data(TARGET_TEST_COURSE, 2)
            df_m2 = df_m2_raw[df_m2_raw["username"] == TARGET_TEST_USER].copy()
            sess_m2 = method_2(df_m2) if not df_m2.empty else pd.DataFrame()

            if not sess_m2.empty:
                sess_m2["username"] = "test_m2"
                sess_m2["display_name"] = TEST_NAME_M2

            if sess_m1.empty and sess_m2.empty:
                sessions = pd.DataFrame()
            else:
                sessions = pd.concat([sess_m1, sess_m2], ignore_index=True)

            if not sessions.empty and start and end:
                start_dt = pd.to_datetime(start)
                end_dt = pd.to_datetime(end) + pd.Timedelta(days=1)
                sessions = sessions[(sessions["fim"] >= start_dt) & (sessions["inicio"] < end_dt)]

            if not sessions.empty and users:
                sessions = sessions[sessions["username"].isin(users)]

            if not sessions.empty:
                sessions = sessions.copy()
                sessions["inicio"] = sessions["inicio"].dt.strftime("%Y-%m-%d %H:%M:%S")
                sessions["fim"] = sessions["fim"].dt.strftime("%Y-%m-%d %H:%M:%S")
                sessions["session_id"] = sessions["sessao_id"]

            users_display = [TEST_NAME_M1, TEST_NAME_M2]
            if users:
                users_display = []
                for u in users:
                    if u == "test_m1":
                        users_display.append(TEST_NAME_M1)
                    elif u == "test_m2":
                        users_display.append(TEST_NAME_M2)
                    else:
                        users_display.append(str(u))

            return {
                "sessions": sessions.to_dict("records") if not sessions.empty else [],
                "users": users_display,
                "start": start,
                "end": end,
            }

        course_id = filters.get("course", 10464) if filters else 10464
        method_key = filters.get("method", "m1") if filters else "m1"
        method_num = 1 if method_key == "m1" else 2

        df_clean = get_clean_data(course_id, method_num)

        if df_clean.empty:
            return {"sessions": [], "users": [], "start": None, "end": None}

        dff = df_clean.copy()

        name_map = dff.set_index("username")["display_name"].to_dict()
        users = filters.get("users", []) if filters else []
        start = filters.get("start") if filters else None
        end = filters.get("end") if filters else None

        if users:
            dff = dff[dff["username"].isin(users)]

        fn = METHODS.get(method_key, method_1)
        sessions = fn(dff)

        if not sessions.empty and start and end:
            start_dt = pd.to_datetime(start)
            end_dt = pd.to_datetime(end) + pd.Timedelta(days=1)
            sessions = sessions[(sessions["fim"] >= start_dt) & (sessions["inicio"] < end_dt)]

        if not sessions.empty:
            sessions = sessions.copy()
            sessions["display_name"] = sessions["username"].map(name_map)
            sessions["inicio"] = sessions["inicio"].dt.strftime("%Y-%m-%d %H:%M:%S")
            sessions["fim"] = sessions["fim"].dt.strftime("%Y-%m-%d %H:%M:%S")
            sessions["session_id"] = sessions["sessao_id"]

        users_display = [name_map.get(u, str(u)) for u in (users or [])]

        return {
            "sessions": sessions.to_dict("records") if not sessions.empty else [],
            "users": users_display,
            "start": start,
            "end": end,
        }

    @app.callback(
        Output("graph-2", "figure"),
        Input("sessions-store", "data"),
    )
    def update_graphs(payload):
        payload = payload or {"sessions": [], "users": [], "start": None, "end": None}
        fig2 = fig_week_bars(payload)
        return fig2