import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def fig_gantt_sessions(payload):
    sessions = pd.DataFrame(payload.get("sessions", []) or [])
    users_display = payload.get("users", []) or []
    start = payload.get("start")
    end = payload.get("end")

    # ===== VISUAL =====
    ROW_HEIGHT = 85
    BASE_HEIGHT = 140
    FIG_MIN_HEIGHT = 300
    BARGAP = 0.55

    # ===== Sessões curtas: mínimo visível proporcional a 5 min =====
    MIN_SESSION_MIN = 5              # regra: <5min vira mínimo visível
    MIN_PX = 10                      # (se quiser ignorar px, deixe MIN_PX=0)
    ASSUMED_PLOT_WIDTH_PX = 900
    MAX_MIN_DURATION_MIN = 30

    if not start or not end:
        fig = go.Figure()
        fig.add_annotation(text="Selecione um dia ou período no calendário", showarrow=False)
        fig.update_layout(height=FIG_MIN_HEIGHT, margin=dict(l=10, r=10, t=20, b=10))
        return fig

    start_dt = pd.to_datetime(start)
    end_dt = pd.to_datetime(end) + pd.Timedelta(days=1)

    if not users_display:
        fig = go.Figure()
        fig.add_annotation(text="Selecione pelo menos um aluno", showarrow=False)
        fig.update_layout(height=FIG_MIN_HEIGHT, margin=dict(l=10, r=10, t=20, b=10))
        return fig

    height = max(FIG_MIN_HEIGHT, BASE_HEIGHT + ROW_HEIGHT * len(users_display))

    if not sessions.empty:
        sessions = sessions.copy()
        sessions["inicio"] = pd.to_datetime(sessions["inicio"])
        sessions["fim"] = pd.to_datetime(sessions["fim"])
        sessions["kind"] = "session"
        sessions["session_label"] = sessions["session_id"].apply(lambda x: f"Sessão {int(x)}")
    else:
        sessions = pd.DataFrame(
            columns=["display_name", "inicio", "fim", "kind", "session_label", "username", "session_id"]
        )

    axis_range = end_dt - start_dt

    if MIN_PX > 0:
        approx_from_px = axis_range * (MIN_PX / ASSUMED_PLOT_WIDTH_PX)
        approx_from_px = min(approx_from_px, pd.Timedelta(minutes=MAX_MIN_DURATION_MIN))
    else:
        approx_from_px = pd.Timedelta(0)

    min_duration = max(pd.Timedelta(minutes=MIN_SESSION_MIN), approx_from_px)

    if not sessions.empty:
        dur = sessions["fim"] - sessions["inicio"]
        sessions["fim_plot"] = sessions["fim"]
        mask = dur < pd.Timedelta(minutes=MIN_SESSION_MIN)
        sessions.loc[mask, "fim_plot"] = sessions.loc[mask, "inicio"] + min_duration
        sessions["inicio_str"] = sessions["inicio"].dt.strftime("%d/%m/%Y %H:%M")
        sessions["fim_str"] = sessions["fim"].dt.strftime("%d/%m/%Y %H:%M")
    else:
        sessions["fim_plot"] = sessions["fim"]
        sessions["inicio_str"] = pd.Series(dtype="object")
        sessions["fim_str"] = pd.Series(dtype="object")

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
            "session_id": [None] * len(no_session_users),
            "inicio_str": [start_dt.strftime("%d/%m/%Y %H:%M")] * len(no_session_users),
            "fim_str": [end_dt.strftime("%d/%m/%Y %H:%M")] * len(no_session_users),
        })
        plot_df = pd.concat([sessions, df_no], ignore_index=True)
    else:
        plot_df = sessions

    if plot_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Sem dados para o período selecionado", showarrow=False)
        fig.update_layout(height=height, margin=dict(l=10, r=10, t=20, b=10))
        return fig

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
            tr.hovertemplate = None
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

    fig.update_layout(
        height=height,
        bargap=BARGAP,
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=False,
    )

    return fig