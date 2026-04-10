import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def _empty_fig(msg, height=420):
    fig = go.Figure()
    fig.add_annotation(text=msg, showarrow=False)
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=20, b=10))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig

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
    MIN_SESSION_MIN = 5              
    MIN_PX = 10                      
    ASSUMED_PLOT_WIDTH_PX = 900
    MAX_MIN_DURATION_MIN = 30

    if not start or not end:
        return _empty_fig("Selecione um dia ou período no calendário", height=FIG_MIN_HEIGHT)

    start_dt = pd.to_datetime(start)
    end_dt = pd.to_datetime(end) + pd.Timedelta(days=1)

    if not users_display:
        return _empty_fig("Selecione pelo menos um aluno", height=FIG_MIN_HEIGHT)

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
        return _empty_fig("Sem dados para o período selecionado", height=height)

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

    limiar = pd.Timedelta(minutes=5)
    minimo_visual = pd.Timedelta(minutes=5)
    dur = sessions["fim"] - sessions["inicio"]
    sessions["fim_plot"] = sessions["fim"]
    mask = dur < limiar
    sessions.loc[mask, "fim_plot"] = sessions.loc[mask, "inicio"] + minimo_visual

    sessions["dia"] = sessions["inicio"].dt.normalize()
    sessions["start_min"] = sessions["inicio"].dt.hour * 60 + sessions["inicio"].dt.minute + sessions["inicio"].dt.second / 60.0
    sessions["dur_min"] = (sessions["fim_plot"] - sessions["inicio"]).dt.total_seconds() / 60.0
    
    # Previne erro se a coluna se chamar session_id ou sessao_id
    id_col = "session_id" if "session_id" in sessions.columns else "sessao_id"
    sessions["session_label"] = sessions[id_col].apply(lambda x: f"Sessão {int(x)}")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=sessions["dia"],               
        x=sessions["dur_min"],           
        base=sessions["start_min"],      
        orientation='h',                 
        width=0.60 * 24 * 60 * 60 * 1000, 
        marker=dict(color="#3B82F6"),
        hovertemplate=f"<b>{aluno}</b><br>%{{customdata[0]}}<br>Início: %{{customdata[1]}}<br>Fim: %{{customdata[2]}}<extra></extra>",
        customdata=sessions[["session_label", "inicio", "fim"]].astype(str).to_numpy(),
    ))

    fig.update_layout(
        height=height, 
        margin=dict(l=10, r=10, t=50, b=10), 
        showlegend=False, 
        plot_bgcolor="white"
    )
    
    fig.update_xaxes(
        range=[0, 24 * 60], 
        tickvals=list(range(0, 24 * 60 + 1, 120)), 
        ticktext=[f"{h:02d}:00" for h in range(0, 25, 2)],
        title="Hora do Dia",
        gridcolor="#E5E7EB"
    )
    
    fig.update_yaxes(
        autorange="reversed", 
        tickformat="%d/%b",   
        title="Data",
        gridcolor="#E5E7EB"
    )
    
    return fig