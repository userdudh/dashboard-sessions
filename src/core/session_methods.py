import pandas as pd

def _aggregate_sessions(df):
    if df.empty: return pd.DataFrame()

    EVENTOS_TRADUZIDOS = {
        "course_vis": "Acessou a disciplina",
        "assignment_vis": "Visualizou atividade",
        "forum_vis": "Acessou o fórum",
        "resource_vis": "Acessou o material",
        "assignment_try": "Iniciou atividade",
        "assignment_sub": "Submeteu atividade",
        "forum_participation": "Postou no fórum",
        "message_read": "Leu mensagem",
        "message_sent": "Enviou mensagem",
    }

    def formatar_eventos(series):
        eventos = series[series != "course_vis"]
        if eventos.empty:
            return "Apenas eventos de acesso a disciplina nesta sessão"
        
        contagem = eventos.value_counts()
        return "<br>".join([f"{EVENTOS_TRADUZIDOS.get(cls, cls)}: {qtd}" for cls, qtd in contagem.items() if qtd > 0])

    dataframe = (
        df.groupby(["username", "sessao_id"], as_index=False)
          .agg(
              inicio=("datetime", "min"),
              fim=("datetime", "max"),
              eventos_resumo=("class", formatar_eventos)
          )
    )
    return dataframe

def method_1(df): return _aggregate_sessions(df)
def method_2(df): return _aggregate_sessions(df)