import pandas as pd
from dash import Input, Output
from src.core.session_methods import method_1, method_2, method_3

# Importamos os gráficos do ficheiro de componentes visuais
from src.ui.components.charts import fig_gantt_sessions, fig_week_bars

METHODS = {"m1": method_1, "m2": method_2, "m3": method_3}

# Alturas e espaçamentos base para o cálculo dinâmico do gráfico 1
MIN_GRAPH1_HEIGHT = 300 
ROW_HEIGHT = 85
BASE_HEIGHT = 140

def register_charts_callbacks(app, dfs):
    
    @app.callback(
        Output("sessions-store", "data"),
        Input("filters-store", "data"),
    )
    def compute_sessions(filters):
        if not filters:
            return {"sessions": [], "users": [], "start": None, "end": None}

        method_key = filters.get("method", "m1")
        
        df_clean = dfs.get(method_key)

        if df_clean is None or df_clean.empty:
            return {"sessions": [], "users": [], "start": None, "end": None}

        name_map = df_clean.set_index("username")["display_name"].to_dict()
        course = filters.get("course") 
        users = filters.get("users", [])
        start = filters.get("start")
        end = filters.get("end")

        dff = df_clean
        
        # 1. Filtro pelo curso selecionado na sidebar
        if course:
            dff = dff[dff["courseid"] == course] 
            
        # 2. Filtro pelos alunos selecionados
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
            
            # Garantir a compatibilidade caso a coluna se chame sessao_id ou session_id
            if "sessao_id" in sessions.columns and "session_id" not in sessions.columns:
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
        
        # Geramos as figuras usando as funções importadas do charts.py
        fig1 = fig_gantt_sessions(payload)
        fig2 = fig_week_bars(payload, height=560)

        # Calculamos a altura dinâmica do primeiro gráfico consoante o número de alunos
        height_g1 = max(MIN_GRAPH1_HEIGHT, BASE_HEIGHT + ROW_HEIGHT * len(users_display))

        # Estilos para esconder/mostrar as abas dos gráficos
        style_g1 = {"height": f"{height_g1}px", "display": "block" if active_tab == "g1" else "none"}
        style_g2 = {"height": "560px", "display": "block" if active_tab == "g2" else "none"}

        return fig1, style_g1, fig2, style_g2