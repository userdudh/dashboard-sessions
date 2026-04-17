from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

def make_course_options(df):
    if "courseid" not in df.columns:
        return []
    courses = df["courseid"].dropna().unique()
    return [{"label": f"Curso {c}", "value": c} for c in sorted(courses)]

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
                dbc.Label("Curso:"),
                dcc.Dropdown(
                    id="course-select",
                    options=[
                    {"label": "Curso 10464", "value": 10464},
                    {"label": "Curso 8288", "value": 8288},
                    {"label": "Curso 6744", "value": 6744},
                    {"label": "Curso 5282", "value": 5282},
                    {"label": "Curso 1", "value": 1},
                    ],
                    value=10464,
                    clearable=False,
                    className="full-width-input"
                ),

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
                    className="full-width-input"
                ),

                html.Div(style={"height": "14px"}),

                dbc.Label("Alunos:"),
                dcc.Dropdown(
                    id="users-select",
                    options=make_user_options(df),
                    value=None, 
                    multi=False, 
                    placeholder="Selecione um aluno",
                    className="full-width-input"
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