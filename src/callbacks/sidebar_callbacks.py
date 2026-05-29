from dash import Input, Output, State, ctx

from src.core.preprocess import get_clean_data
from src.core.modetests import SPECIAL_MODES, get_mode_options


def register_sidebar_callbacks(app, _):

    @app.callback(
        [
            Output("logs-lock-store", "data"),
            Output("app-mode-switch", "options"),
            Output("app-mode-switch", "value"),
            Output("logs-lock-icon", "children"),
            Output("logs-lock-button", "title"),
        ],
        Input("logs-lock-button", "n_clicks"),
        [
            State("logs-lock-store", "data"),
            State("app-mode-switch", "value"),
        ],
    )
    def toggle_logs_lock(n_clicks, lock_data, current_mode):
        locked = False

        if isinstance(lock_data, dict):
            locked = lock_data.get("locked", False)

        if ctx.triggered_id == "logs-lock-button":
            locked = not locked

        options = [
            {"label": "Modo Treinamento", "value": "train"},
            {"label": "Modo Experimento", "value": "test"},
            {
                "label": "Dashboard Geral",
                "value": "full",
                "disabled": locked,
            },
        ]

        selected_mode = current_mode or "train"

        if locked and selected_mode == "full":
            selected_mode = "train"

        icon = "lock" if locked else "lock_open"

        title = (
            "Logs internos bloqueado"
            if locked
            else "Logs internos desbloqueado"
        )

        return {"locked": locked}, options, selected_mode, icon, title

    @app.callback(
        [
            Output("navbar-container", "style"),
            Output("order-container", "style"),
            Output("course-select", "disabled"),
        ],
        Input("app-mode-switch", "value"),
    )
    def toggle_mode_ui(mode):
        if mode in SPECIAL_MODES:
            return {"display": "none"}, {"display": "none"}, True

        return {"display": "block"}, {"display": "block"}, False

    @app.callback(
        [
            Output("users-select", "options"),
            Output("users-select", "value"),
        ],
        [
            Input("course-select", "value"),
            Input("order-select", "value"),
            Input("method-tabs", "active_tab"),
            Input("app-mode-switch", "value"),
        ],
        State("users-select", "value"),
    )
    def update_sidebar(course, order_value, active_method, mode, current_selected_users):

        if mode in SPECIAL_MODES:
            options = get_mode_options(mode)

            valid_values = {option["value"] for option in options}

            if current_selected_users in valid_values:
                selected = current_selected_users
            else:
                selected = None

            return options, selected

        current_course = course if course else 2060
        method_num = 2 if active_method == "m2" else 1

        df_current = get_clean_data(current_course, method_num)

        if df_current.empty:
            return [], None

        base = df_current[["username", "display_name"]].drop_duplicates().copy()

        if order_value in ["most_sessions", "least_sessions"]:
            counts = df_current["username"].value_counts()
            base["count"] = base["username"].map(counts)

            ordered = base.sort_values(
                "count",
                ascending=(order_value == "least_sessions"),
            )
        else:
            ordered = base.sort_values("display_name", ascending=True)

        options = [
            {
                "label": row["display_name"],
                "value": row["username"],
            }
            for _, row in ordered.iterrows()
        ]

        trigger = ctx.triggered_id

        if trigger in ["course-select", "app-mode-switch"]:
            new_value = None
        else:
            valid_values = {option["value"] for option in options}
            new_value = (
                current_selected_users
                if current_selected_users in valid_values
                else None
            )

        return options, new_value

    @app.callback(
        Output("filters-store", "data"),
        [
            Input("method-tabs", "active_tab"),
            Input("course-select", "value"),
            Input("users-select", "value"),
            Input("date-reserva", "value"),
        ],
        State("order-select", "value"),
    )
    def build_filters(method, course, users, date_value, order):
        start, end = None, None

        if date_value and len(date_value) == 2:
            start = date_value[0]
            end = date_value[1] or date_value[0]

        users_list = [users] if users else []

        return {
            "method": method or "m1",
            "course": course if course else 2060,
            "order": order,
            "users": users_list,
            "start": start,
            "end": end,
        }
    