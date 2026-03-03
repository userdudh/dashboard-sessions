from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc


def make_user_options(df):
    users_df = (
        df[["username", "display_name"]]
        .drop_duplicates()
        .sort_values("display_name")
    )

    options = [
        {"label": row["display_name"], "value": row["username"]}
        for _, row in users_df.iterrows()
    ]
    return options


def sidebar(df):
    return dbc.Card(
        dbc.CardBody(
            [
                dbc.Label("Ordenar alunos:"),
                dcc.Dropdown(
                    id="order-select",
                    options=[
                        {"label": "Mais sessões", "value": "most_sessions"},
                        {"label": "Menos sessões", "value": "least_sessions"},
                        {"label": "A–Z", "value": "az"},
                    ],
                    value="most_sessions",
                    clearable=False,
                ),

                html.Div(style={"height": "14px"}),

                dbc.Label("Alunos:"),
                dcc.Dropdown(
                    id="users-select",
                    options=make_user_options(df),
                    value=[],
                    multi=True,
                    placeholder="Selecione alunos",
                ),

                html.Div(style={"height": "14px"}),

                dbc.Label("Data:"),
                dmc.DatePicker(
                    id="date-reserva",
                    type="range",
                    numberOfColumns=1,              
                    allowSingleDateInRange=True,    
                    allowDeselect=True,             
                    style={"width": "100%"},
                    minDate="2014-12-04",
                    maxDate="2017-01-10",
                    defaultDate="2016-08-24",
                ),

                dcc.Store(id="date-memory"),
                dcc.Store(id="filters-store"),
            ]
        ),
        className="h-100",
    )