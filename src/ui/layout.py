import dash_mantine_components as dmc
from dash import dcc, html
import dash_bootstrap_components as dbc
from src.ui.components.sidebar import sidebar

def create_layout(df):
    return dmc.MantineProvider(
        children=dbc.Container(
            fluid=True,
            children=[
                dbc.Card(
                    dbc.CardBody(
                        html.Div(
                            className="navbar-flex",
                            children=[
                                html.Div(
                                    html.Span("insert_chart", className="material-symbols-outlined"),
                                    className="nav-icon-box"
                                ),
                                dbc.Tabs(
                                    id="method-tabs",
                                    active_tab="m1",
                                    className="custom-tabs",
                                    children=[
                                        dbc.Tab(label="Método 1", tab_id="m1"),
                                        dbc.Tab(label="Método 2", tab_id="m2"),
                                    ],
                                )
                            ]
                        )
                    ),
                    className="mb-3 navbar-card",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            sidebar(df), 
                            className="sidebar-container d-flex flex-column"
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        dcc.Store(id="sessions-store"),
                                        dcc.Graph(id="graph-2"),
                                    ]
                                ),
                                className="h-100" 
                            ),
                            className="chart-container d-flex flex-column"
                        ),
                    ],
                    className="g-3 dashboard-row",
                ),
            ],
            className="py-3",
        )
    )