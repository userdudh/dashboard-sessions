from dash import Input, Output, State, no_update
import pandas as pd
from src.core.load import data_loader
from src.core.preprocess import preprocess

def register_sidebar_callbacks(app, _):

    @app.callback(
        [Output("users-select", "options"),
         Output("users-select", "value")],
        [Input("course-select", "value"),
         Input("order-select", "value"),
         Input("method-tabs", "active_tab")],
        [State("users-select", "value"), # Captura o estado atual dos usuários selecionados
         State("course-select", "value")] # Para comparar se o curso realmente mudou
    )
    def update_sidebar(course, order_value, active_method, current_selected_users, last_course):
        # Define o curso atual
        current_course = course if course else 10464
        method_num = 2 if active_method == "m2" else 1
        
        # Carrega os dados do curso/método
        df_raw = data_loader(current_course, method_num)
        df_current = preprocess(df_raw)
        
        if df_current.empty:
            return [], []

        # Prepara as opções do Dropdown
        base = df_current[["username", "display_name"]].drop_duplicates().copy()
        
        # Ordenação
        if order_value == "most_sessions":
            counts = df_current["username"].value_counts()
            base["count"] = base["username"].map(counts)
            ordered = base.sort_values("count", ascending=False)
        else:
            ordered = base.sort_values("display_name", ascending=True)

        options = [{"label": r["display_name"], "value": r["username"]} for _, r in ordered.iterrows()]
        
        # LÓGICA DE PERSISTÊNCIA:
        # Se o curso for o mesmo de antes, mantemos os usuários selecionados
        # Se o curso mudou, limpamos a seleção (pois são outros alunos)
        if course == last_course:
            new_value = current_selected_users if current_selected_users else []
        else:
            new_value = []

        return options, new_value

    @app.callback(
        Output("filters-store", "data"),
        [Input("method-tabs", "active_tab"),
         Input("course-select", "value"), 
         Input("users-select", "value"),
         Input("date-reserva", "value")],
        [State("order-select", "value")]
    )
    def build_filters(method, course, users, date_value, order):
        start, end = None, None
        if date_value and len(date_value) == 2:
            start = date_value[0]
            end = date_value[1] or date_value[0]

        return {
            "method": method or "m1",
            "course": course if course else 10464,
            "order": order,
            "users": users or [], # Lista vazia se nada for selecionado
            "start": start,
            "end": end,
        }