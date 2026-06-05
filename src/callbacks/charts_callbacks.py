import pandas as pd
from dash import Input, Output
from dash.exceptions import PreventUpdate

from src.core.session_methods import method_1, method_2
from src.core.preprocess import get_clean_data
from src.core.modetests import (
    SPECIAL_MODES,
    get_special_mode_sessions,
    get_label_by_value,
)
from src.ui.components.charts import fig_week_bars

METHODS = {
    "m1": method_1,
    "m2": method_2,
}

def register_charts_callbacks(app, _):

    @app.callback(
        Output("sessions-store", "data"),
        [
            Input("filters-store", "data"),
            Input("app-mode-switch", "value"),
        ],
    )
    def compute_sessions(filters, mode):
        if not filters:
            raise PreventUpdate

        start = filters.get("start")
        end = filters.get("end")
        users = filters.get("users", [])

        if not start or not end:
            raise PreventUpdate

        if len(users) != 1:
            return {
                "sessions": [],
                "users": [],
                "start": start,
                "end": end,
            }

        if mode in SPECIAL_MODES:
            sessions = get_special_mode_sessions(mode, course_id=2060).copy()

            if not sessions.empty:
                sessions = sessions[sessions["username"].isin(users)]

            if not sessions.empty:
                start_dt = pd.to_datetime(start)
                end_dt = pd.to_datetime(end) + pd.Timedelta(days=1)

                sessions = sessions[
                    (sessions["fim"] >= start_dt)
                    & (sessions["inicio"] < end_dt)
                ]

            label_by_value = get_label_by_value(mode)

            users_display = [
                label_by_value[user]
                for user in users
                if user in label_by_value
            ]

            if not sessions.empty:
                sessions["inicio"] = (
                    pd.to_datetime(sessions["inicio"], errors="coerce")
                    .dt.strftime("%Y-%m-%d %H:%M:%S")
                )
                sessions["fim"] = (
                    pd.to_datetime(sessions["fim"], errors="coerce")
                    .dt.strftime("%Y-%m-%d %H:%M:%S")
                )

            return {
                "sessions": sessions.to_dict("records") if not sessions.empty else [],
                "users": users_display,
                "start": start,
                "end": end,
            }

        course_id = filters.get("course", 2060)
        method_key = filters.get("method", "m1")
        method_num = 1 if method_key == "m1" else 2

        df_clean = get_clean_data(course_id, method_num)

        if df_clean.empty:
            return {
                "sessions": [],
                "users": [],
                "start": start,
                "end": end,
            }

        name_map = df_clean.set_index("username")["display_name"].to_dict()

        dff = df_clean[df_clean["username"].isin(users)]

        start_dt = pd.to_datetime(start)
        end_dt = pd.to_datetime(end) + pd.Timedelta(days=1)

        dff = dff[
            (dff["datetime"] >= start_dt)
            & (dff["datetime"] < end_dt)
        ]

        if dff.empty:
            users_display = [
                name_map.get(user, str(user))
                for user in users
            ]

            return {
                "sessions": [],
                "users": users_display,
                "start": start,
                "end": end,
            }

        fn = METHODS.get(method_key, method_1)
        sessions = fn(dff)

        if not sessions.empty:
            sessions = sessions.copy()
            sessions["display_name"] = sessions["username"].map(name_map)
            sessions["inicio"] = sessions["inicio"].dt.strftime("%Y-%m-%d %H:%M:%S")
            sessions["fim"] = sessions["fim"].dt.strftime("%Y-%m-%d %H:%M:%S")
            sessions["session_id"] = sessions["sessao_id"]

        users_display = [
            name_map.get(user, str(user))
            for user in users
        ]

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
        payload = payload or {
            "sessions": [],
            "users": [],
            "start": None,
            "end": None,
        }

        return fig_week_bars(payload)