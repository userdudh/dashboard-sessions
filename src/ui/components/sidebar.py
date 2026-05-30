from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

def make_user_options(df):
    if df.empty or "username" not in df.columns:
        return []

    users_df = (
        df[["username", "display_name"]]
        .drop_duplicates()
        .sort_values("display_name")
    )

    return [
        {
            "label": row["display_name"],
            "value": row["username"],
        }
        for _, row in users_df.iterrows()
    ]

def make_course_options(df):
    if "courseid" not in df.columns:
        return []

    courses = df["courseid"].dropna().unique()

    return [
        {"label": f"Curso {c}", "value": c}
        for c in sorted(courses)
    ]

def sidebar(df):
    return dbc.Card(
        dbc.CardBody(
            [
                dbc.Label("Curso:"),
                dcc.Dropdown(
                    id="course-select",
                    options=[
                        {"label": "Curso 2060", "value": 2060},
                    ],
                    value=2060,
                    clearable=False,
                    className="full-width-input",
                ),

                html.Div(
                    id="order-container",
                    children=[
                        html.Div(style={"height": "14px"}),

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
                            className="full-width-input",
                        ),
                    ],
                ),

                html.Div(style={"height": "14px"}),

                dbc.Label("Alunos:"),
                dcc.Dropdown(
                    id="users-select",
                    options=make_user_options(df),
                    value=None,
                    multi=False,
                    placeholder="Selecione um aluno",
                    className="full-width-input",
                ),

                html.Div(style={"height": "14px"}),

                dbc.Label("Data:"),
                dmc.DatePicker(
                    id="date-reserva",
                    type="range",
                    numberOfColumns=1,
                    allowSingleDateInRange=True,
                    allowDeselect=True,
                    className="full-width-input",

                    minDate="2019-11-01",
                    maxDate="2019-12-31",
                    defaultDate="2019-11-24",

                    firstDayOfWeek=0,
                    weekendDays=[0, 6],
                
                    styles={
                        "weekday": {
                            "textTransform": "lowercase",
                        },
                    },
                ),

                dcc.Store(id="date-memory"),
                dcc.Store(id="filters-store"),
            ]
        ),
        className="h-100",
    )