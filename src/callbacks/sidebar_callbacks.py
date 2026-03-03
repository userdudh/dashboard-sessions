from dash import Input, Output
import pandas as pd
from src.core.load import data_loader
from src.core.preprocess import preprocess
from src.core.session_methods import method_1

def register_sidebar_callbacks(app, _unused_df):

    @app.callback(
        Output("users-select", "options"),
        Input("order-select", "value"),
        Input("method-tabs", "active_tab"),
    )
    def order_students(order_value, active_method):
        method_num = int(active_method.replace("m", "")) if active_method else 1
        
        df_current = preprocess(data_loader(method_num))
        
        if df_current.empty:
            return []

        sessions_df = method_1(df_current)
        sessions_count = sessions_df.groupby("username").size().to_dict()

        base = (
            df_current[["username", "display_name"]]
            .drop_duplicates()
            .copy()
        )

        base["n_sessions"] = base["username"].map(lambda u: sessions_count.get(u, 0))

        if order_value == "most_sessions":
            ordered = base.sort_values(["n_sessions", "display_name"], ascending=[False, True])
        elif order_value == "least_sessions":
            ordered = base.sort_values(["n_sessions", "display_name"], ascending=[True, True])
        else:
            ordered = base.sort_values("display_name", ascending=True)

        return [
            {"label": r["display_name"], "value": r["username"]}
            for _, r in ordered.iterrows()
        ]

    @app.callback(
        Output("filters-store", "data"),
        Input("method-tabs", "active_tab"),
        Input("order-select", "value"),
        Input("users-select", "value"),
        Input("date-reserva", "value"),
    )
    def build_filters(method, order, users, date_value):
        start = None
        end = None

        if date_value and len(date_value) == 2:
            start = date_value[0]
            end = date_value[1] or date_value[0]

        return {
            "method": method or "m1",
            "order": order,
            "users": users or [],
            "start": start,
            "end": end,
        }