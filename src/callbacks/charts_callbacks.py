import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output

from src.core.load import data_loader
from src.core.preprocess import preprocess
from src.core.session_methods import method_1, method_2, method_3

METHODS = {"m1": method_1, "m2": method_2, "m3": method_3}

# =========================
# CONFIG VISUAL
# =========================
MIN_GRAPH1_HEIGHT = 700
ROW_HEIGHT = 85
BASE_HEIGHT = 140
BARGAP = 0.55

# ==============================
# CONFIG SESSÕES CURTAS
# ==============================
LIMIAR_MINUTOS = 5
DURACAO_MINIMA_VISUAL_MINUTOS = 5


def _empty_fig(msg, height=420):
    fig = go.Figure()
    fig.add_annotation(text=msg, showarrow=False)
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=20, b=10))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def fig_gantt_sessions(payload, height=MIN_GRAPH1_HEIGHT):
    sessions = pd.DataFrame(payload.get("sessions", []) or [])
    users_display = payload.get("users", []) or []
    start = payload.get("start")
    end = payload.get("end")

    if not start or not end:
        return _empty_fig("Selecione um dia ou período no calendário", height=height)

    start_dt = pd.to_datetime(start)
    end_dt = pd.to_datetime(end) + pd.Timedelta(days=1)

    if not users_display:
        return _empty_fig("Selecione pelo menos um aluno", height=height)

    if not sessions.empty:
        sessions = sessions.copy()
        sessions["inicio"] = pd.to_datetime(sessions["inicio"])
        sessions["fim"] = pd.to_datetime(sessions["fim"])
        sessions["kind"] = "session"
        sessions["session_label"] = sessions["sessao_id"].apply(lambda x: f"Sessão {int(x)}")
        sessions["inicio_str"] = sessions["inicio"].dt.strftime("%d/%m/%Y %H:%M")
        sessions["fim_str"] = sessions["fim"].dt.strftime("%d/%m/%Y %H:%M")
    else:
        sessions = pd.DataFrame(
            columns=[
                "display_name", "inicio", "fim", "kind",
                "session_label", "username", "sessao_id",
                "inicio_str", "fim_str"
            ]
        )

    limiar = pd.Timedelta(minutes=LIMIAR_MINUTOS)
    minimo_visual = pd.Timedelta(minutes=DURACAO_MINIMA_VISUAL_MINUTOS)

    if not sessions.empty:
        dur = sessions["fim"] - sessions["inicio"]
        sessions["fim_plot"] = sessions["fim"]
        mask = dur < limiar
        sessions.loc[mask, "fim_plot"] = sessions.loc[mask, "inicio"] + minimo_visual
    else:
        sessions["fim_plot"] = sessions["fim"]

    users_with_sessions = set(sessions["display_name"].unique()) if not sessions.empty else set()
    no_session_users = [u for u in users_display if u not in users_with_sessions]

    if no_session_users:
        df_no = pd.DataFrame({
            "display_name": no_session_users,
            "inicio": [start_dt] * len(no_session_users),
            "fim": [end_dt] * len(no_session_users),
            "fim_plot": [end_dt] * len(no_session_users),
            "kind": ["no_session"] * len(no_session_users),
            "session_label": ["ALUNO SEM SESSÕES NO PERÍODO"] * len(no_session_users),
            "username": [None] * len(no_session_users),
            "sessao_id": [None] * len(no_session_users),
            "inicio_str": [start_dt.strftime("%d/%m/%Y %H:%M")] * len(no_session_users),
            "fim_str": [end_dt.strftime("%d/%m/%Y %H:%M")] * len(no_session_users),
        })
        plot_df = pd.concat([sessions, df_no], ignore_index=True)
    else:
        plot_df = sessions

    fig = px.timeline(
        plot_df,
        x_start="inicio",
        x_end="fim_plot",
        y="display_name",
        color="kind",
        color_discrete_map={"session": "#3B82F6", "no_session": "#BDBDBD"},
    )

    fig.update_traces(text=None, hovertemplate=None, customdata=None)

    for tr in fig.data:
        if tr.name == "no_session":
            tr.text = ["ALUNO SEM SESSÕES NO PERÍODO"] * len(tr.x)
            tr.textposition = "inside"
            tr.insidetextanchor = "middle"
            tr.textfont = dict(color="black", size=12)
            tr.hoverinfo = "skip"
        elif tr.name == "session":
            session_rows = plot_df[plot_df["kind"] == "session"][["session_label", "inicio_str", "fim_str"]].to_numpy()
            tr.customdata = session_rows
            tr.hovertemplate = (
                "<b>%{y}</b><br>"
                "%{customdata[0]}<br>"
                "Início: %{customdata[1]}<br>"
                "Fim: %{customdata[2]}<extra></extra>"
            )

    fig.update_yaxes(
        categoryorder="array",
        categoryarray=users_display,
        autorange="reversed",
        title="Usuário",
    )
    fig.update_xaxes(range=[start_dt, end_dt], title="Tempo")
    fig.update_layout(height=height, bargap=BARGAP, margin=dict(l=10, r=10, t=20, b=10), showlegend=False)

    return fig


def fig_week_bars(payload, height=520):
    sessions = pd.DataFrame(payload.get("sessions", []) or [])
    users_display = payload.get("users", []) or []
    start = payload.get("start")
    end = payload.get("end")

    if not start or not end or not users_display or len(users_display) != 1:
        return _empty_fig("Selecione exatamente 1 aluno no calendário", height=height)

    aluno = users_display[0]
    if sessions.empty:
        return _empty_fig("Sem sessões para o aluno no período", height=height)

    sessions = sessions.copy()
    sessions["inicio"] = pd.to_datetime(sessions["inicio"])
    sessions["fim"] = pd.to_datetime(sessions["fim"])

    if "display_name" in sessions.columns:
        sessions = sessions[sessions["display_name"] == aluno]

    if sessions.empty:
        return _empty_fig("Sem sessões para o aluno no período", height=height)

    limiar = pd.Timedelta(minutes=LIMIAR_MINUTOS)
    minimo_visual = pd.Timedelta(minutes=DURACAO_MINIMA_VISUAL_MINUTOS)
    dur = sessions["fim"] - sessions["inicio"]
    sessions["fim_plot"] = sessions["fim"]
    mask = dur < limiar
    sessions.loc[mask, "fim_plot"] = sessions.loc[mask, "inicio"] + minimo_visual

    sessions["dia"] = sessions["inicio"].dt.normalize()
    sessions["start_min"] = sessions["inicio"].dt.hour * 60 + sessions["inicio"].dt.minute + sessions["inicio"].dt.second / 60.0
    sessions["dur_min"] = (sessions["fim_plot"] - sessions["inicio"]).dt.total_seconds() / 60.0
    sessions["session_label"] = sessions["sessao_id"].apply(lambda x: f"Sessão {int(x)}")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=sessions["dia"],
        y=sessions["dur_min"],
        base=sessions["start_min"],
        width=0.60 * 24 * 60 * 60 * 1000,
        marker=dict(color="#3B82F6"),
        hovertemplate=f"<b>{aluno}</b><br>%{{customdata[0]}}<br>Início: %{{customdata[1]}}<br>Fim: %{{customdata[2]}}<extra></extra>",
        customdata=sessions[["session_label", "inicio", "fim"]].astype(str).to_numpy(),
    ))

    fig.update_layout(height=height, margin=dict(l=10, r=10, t=50, b=10), showlegend=False, plot_bgcolor="white")
    fig.update_yaxes(range=[24 * 60, 0], tickvals=list(range(0, 24 * 60, 60)), ticktext=[f"{h:02d}:00" for h in range(24)])
    return fig


def register_charts_callbacks(app, _unused_df):
    @app.callback(
        Output("sessions-store", "data"),
        Input("filters-store", "data"),
    )
    def compute_sessions(filters):
        if not filters:
            return {"sessions": [], "users": [], "start": None, "end": None}

        method_key = filters.get("method", "m1")
        method_number = int(method_key.replace("m", ""))
        
        df_raw = data_loader(method_number)
        df_clean = preprocess(df_raw)

        if df_clean.empty:
            return {"sessions": [], "users": [], "start": None, "end": None}

        name_map = df_clean.set_index("username")["display_name"].to_dict()
        users = filters.get("users", [])
        start = filters.get("start")
        end = filters.get("end")

        dff = df_clean
        if users:
            dff = dff[dff["username"].isin(users)]

        if start and end:
            start_dt = pd.to_datetime(start)
            end_dt = pd.to_datetime(end) + pd.Timedelta(days=1)
            dff = dff[(dff["datetime"] >= start_dt) & (dff["datetime"] < end_dt)]

        fn = METHODS.get(method_key, method_1)
        sessions = fn(dff)

        if not sessions.empty:
            sessions = sessions.copy()
            sessions["display_name"] = sessions["username"].map(name_map)
            sessions["inicio"] = sessions["inicio"].dt.strftime("%Y-%m-%d %H:%M:%S")
            sessions["fim"] = sessions["fim"].dt.strftime("%Y-%m-%d %H:%M:%S")

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
        height_g1 = max(MIN_GRAPH1_HEIGHT, BASE_HEIGHT + ROW_HEIGHT * len(users_display))

        fig1 = fig_gantt_sessions(payload, height=height_g1)
        fig2 = fig_week_bars(payload, height=560)

        style_g1 = {"height": f"{height_g1}px", "display": "block" if active_tab == "g1" else "none"}
        style_g2 = {"height": "560px", "display": "block" if active_tab == "g2" else "none"}

        return fig1, style_g1, fig2, style_g2