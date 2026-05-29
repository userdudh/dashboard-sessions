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
        return _empty_fig("Selecione 1 aluno e um periodo no calendário", height=height)

    aluno = users_display[0]

    start_dt = pd.to_datetime(start).normalize()
    end_dt = pd.to_datetime(end).normalize()
    full_date_range = pd.date_range(start=start_dt, end=end_dt, freq="D")

    dynamic_height = max(len(full_date_range) * 70 + 50, 300)

    fig = go.Figure()

    if not sessions.empty:
        sessions = sessions.copy()
        sessions["inicio"] = pd.to_datetime(sessions["inicio"])
        sessions["fim"] = pd.to_datetime(sessions["fim"])

        if "display_name" in sessions.columns:
            sessions = sessions[sessions["display_name"] == aluno]
        elif "username" in sessions.columns:
            sessions = sessions[sessions["username"] == aluno]

        if not sessions.empty:
            limiar = pd.Timedelta(minutes=5)
            minimo_visual = pd.Timedelta(minutes=5)

            dur = sessions["fim"] - sessions["inicio"]

            sessions["fim_plot"] = sessions["fim"]
            mask = dur < limiar
            sessions.loc[mask, "fim_plot"] = (
                sessions.loc[mask, "inicio"] + minimo_visual
            )

            sessions["dia"] = sessions["inicio"].dt.normalize()

            sessions["start_min"] = (
                sessions["inicio"].dt.hour * 60
                + sessions["inicio"].dt.minute
                + sessions["inicio"].dt.second / 60.0
            )

            sessions["dur_min"] = (
                sessions["fim_plot"] - sessions["inicio"]
            ).dt.total_seconds() / 60.0

            sessions["hora_inicio"] = sessions["inicio"].dt.strftime("%H:%M:%S")
            sessions["hora_fim"] = sessions["fim"].dt.strftime("%H:%M:%S")

            def formata_duracao(td):
                ts = int(td.total_seconds())
                h, r = divmod(ts, 3600)
                m, s = divmod(r, 60)
                return f"{h:02d}:{m:02d}:{s:02d}"

            sessions["dur_str"] = (sessions["fim"] - sessions["inicio"]).apply(
                formata_duracao
            )

            if "eventos_resumo" not in sessions.columns:
                sessions["eventos_resumo"] = ""

            sessions["eventos_resumo"] = sessions["eventos_resumo"].fillna("")

    if sessions.empty:
        return _empty_fig("Nenhuma sessão encontrada para esse período", height=height)

    fig.add_trace(
        go.Bar(
            y=sessions["dia"],
            x=sessions["dur_min"],
            base=sessions["start_min"],
            orientation="h",
            width=0.75 * 24 * 60 * 60 * 1000,
            marker=dict(color="#265FA3"),
            hovertemplate=(
                f"<b>{aluno}</b><br>"
                "Período: %{customdata[0]} - %{customdata[1]}<br>"
                "Duração: %{customdata[2]}<br><br>"
                "<b>Eventos</b><br>"
                "%{customdata[3]}<extra></extra>"
            ),
            customdata=sessions[
                ["hora_inicio", "hora_fim", "dur_str", "eventos_resumo"]
            ].to_numpy(),
        )
    )

    weekdays_pt = {
        0: "seg",
        1: "ter",
        2: "qua",
        3: "qui",
        4: "sex",
        5: "sáb",
        6: "dom",
    }

    tickvals = full_date_range
    ticktext = [
        f"{weekdays_pt[d.weekday()]} | {d.strftime('%d/%m')}"
        for d in full_date_range
    ]

    fig.update_layout(
        height=dynamic_height,
        margin=dict(l=10, r=10, t=50, b=10),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="inherit", color="#1F2937"),
    )

    fig.update_xaxes(
        range=[0, 24 * 60],
        tickvals=list(range(0, 24 * 60, 60)),
        ticktext=[f"{h:02d}h" for h in range(24)],
        title="Hora do Dia",
        gridcolor="#E5E7EB",
    )

    fig.update_yaxes(
        tickvals=tickvals,
        ticktext=ticktext,
        range=[
            end_dt + pd.Timedelta(hours=12),
            start_dt - pd.Timedelta(hours=12),
        ],
        title="Data",
        gridcolor="#E5E7EB",
    )

    return fig