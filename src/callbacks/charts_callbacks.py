import pandas as pd
from dash import Input, Output
from src.core.session_methods import method_1, method_2
from src.core.preprocess import get_clean_data
from src.ui.components.charts import fig_gantt_sessions, fig_week_bars

METHODS = {"m1": method_1, "m2": method_2}

MIN_GRAPH1_HEIGHT = 300 
ROW_HEIGHT = 85
BASE_HEIGHT = 140

def register_charts_callbacks(app, _): 
    
    @app.callback(
        Output("sessions-store", "data"),
        Input("filters-store", "data"),
    )
    def compute_sessions(filters):
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
        Output("graph-1", "figure"),
        Output("graph-1", "style"),
        Output("graph-2", "figure"),
        Output("graph-2", "style"),
        Input("sessions-store", "data"),
        Input("chart-tabs", "active_tab"),
    )
    def update_graphs(payload, active_tab):
        payload = payload or {"sessions": [], "users": [], "start": None, "end": None}
        users_display = payload.get("users", []) or []
        
        fig1 = fig_gantt_sessions(payload)
        fig2 = fig_week_bars(payload, height=560)

        height_g1 = max(MIN_GRAPH1_HEIGHT, BASE_HEIGHT + ROW_HEIGHT * len(users_display))

        style_g1 = {"height": f"{height_g1}px", "display": "block" if active_tab == "g1" else "none"}
        style_g2 = {"height": "560px", "display": "block" if active_tab == "g2" else "none"}

        return fig1, style_g1, fig2, style_g2