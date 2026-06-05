import dash_mantine_components as dmc
from dash import dcc, html
import dash_bootstrap_components as dbc

from src.ui.components.sidebar import sidebar

custom_loading_element = html.Div(
    [
        dmc.Loader(
            color="#265fa3",
            size="lg",       
            variant="oval",
            style={"marginBottom": "16px"}
        ),
        html.P("Carregando...", className="loading-spinner-text")
    ],
    className="custom-loading-wrapper"
)

def create_layout(df):
    return dmc.MantineProvider(
        children=dmc.DatesProvider(
            settings={
                "locale": "pt-br",
                "firstDayOfWeek": 0,
                "weekendDays": [0, 6],
            },
            children=dbc.Container(
                fluid=True,
                children=[
                    dcc.Store(
                        id="logs-lock-store",
                        data={"locked": True},
                    ),

                    html.Div(
                        [
                            dcc.RadioItems(
                                id="app-mode-switch",
                                className="mode-switch",
                                options=[
                                    {"label": "Modo Treinamento", "value": "train"},
                                    {"label": "Modo Experimento", "value": "test"},
                                    {
                                        "label": "Dashboard Geral",
                                        "value": "full",
                                        "disabled": True,
                                    },
                                ],
                                value="train",
                                inline=True,
                                inputStyle={
                                    "accentColor": "#265fa3",
                                    "marginRight": "6px",
                                },
                                labelStyle={
                                    "marginRight": "16px",
                                },
                                style={
                                    "paddingLeft": "4px",
                                    "textAlign": "left",
                                },
                            ),

                            html.Button(
                                html.Span(
                                    "lock",
                                    id="logs-lock-icon",
                                    className="material-symbols-outlined",
                                    style={
                                        "fontFamily": "Material Symbols Outlined",
                                        "fontWeight": "normal",
                                        "fontStyle": "normal",
                                        "fontSize": "20px",
                                        "lineHeight": "1",
                                        "letterSpacing": "normal",
                                        "textTransform": "none",
                                        "display": "inline-block",
                                        "whiteSpace": "nowrap",
                                        "wordWrap": "normal",
                                        "direction": "ltr",
                                        "fontFeatureSettings": "'liga'",
                                        "WebkitFontFeatureSettings": "'liga'",
                                        "WebkitFontSmoothing": "antialiased",
                                    },
                                ),
                                id="logs-lock-button",
                                n_clicks=0,
                                title="Logs internos bloqueado",
                                style={
                                    "border": "1px solid #94a3b8",
                                    "backgroundColor": "white",
                                    "borderRadius": "999px",
                                    "width": "34px",
                                    "height": "26px",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                    "cursor": "pointer",
                                    "color": "#334155",
                                    "padding": "0",
                                    "overflow": "hidden",
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "space-between",
                            "backgroundColor": "#f8f9fa",
                            "marginBottom": "10px",
                            "borderRadius": "8px",
                            "padding": "4px 10px",
                        },
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
                                                html.Span(
                                                    "insert_chart",
                                                    className="material-symbols-outlined",
                                                ),
                                                className="nav-icon-box",
                                            ),

                                            dbc.Tabs(
                                                id="method-tabs",
                                                active_tab="m1",
                                                className="custom-tabs",
                                                children=[
                                                    dbc.Tab(
                                                        label="Método 1",
                                                        tab_id="m1",
                                                    ),
                                                    dbc.Tab(
                                                        label="Método 2",
                                                        tab_id="m2",
                                                    ),
                                                ],
                                            ),
                                        ],
                                    )
                                ),
                                className="mb-3 navbar-card",
                            ),
                        ],
                    ),

                    dcc.Loading(
                        id="loading-overlay",
                        fullscreen=True,
                        custom_spinner=custom_loading_element,
                        delay_show=500,
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(
                                        sidebar(df),
                                        className="sidebar-container d-flex flex-column",
                                    ),

                                    dbc.Col(
                                        dbc.Card(
                                            dbc.CardBody(
                                                [
                                                    dcc.Store(id="sessions-store"),
                                                    dcc.Graph(id="graph-2"),
                                                ]
                                            ),
                                            className="h-100",
                                        ),
                                        className="chart-container d-flex flex-column",
                                    ),
                                ],
                                className="g-3 dashboard-row",
                            )
                        ]
                    ),
                ],
                className="py-3",
            ),
        ),
    )