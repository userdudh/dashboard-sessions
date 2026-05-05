import dash_mantine_components as dmc
from dash import dcc, html
import dash_bootstrap_components as dbc
from src.ui.components.sidebar import sidebar

def create_layout(df):
    return dmc.MantineProvider(
        children=dbc.Container(
            fluid=True,
            children=[
                html.Div(
                    dcc.RadioItems(
                        id="app-mode-switch",
                        className="mode-switch",
                        options=[
                            {"label": "Logs internos ", "value": "full"},
                            {"label": "Modo Teste", "value": "test"}
                        ],
                        value="test",
                        inline=True,
                        inputStyle={
                        "accentColor": "#265fa3",
                        "marginRight": "6px"},
                        labelStyle={
                            "marginRight": "16px"},
                        style={"paddingLeft": "10px", "textAlign": "left", "backgroundColor": "#f8f9fa", "marginBottom": "10px", "borderRadius": "8px"}
                    )
                ),
                html.Div(
                    id="navbar-container",
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
                    ]
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