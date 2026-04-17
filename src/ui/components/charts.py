import pandas as pd
import plotly.graph_objects as go

def _empty_fig(msg, height=420):
    fig = go.Figure()
    fig.add_annotation(text=msg, showarrow=False)
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=20, b=10))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
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