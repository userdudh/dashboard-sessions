import dash_mantine_components as dmc
from dash import dcc
import dash_bootstrap_components as dbc
from src.ui.components.sidebar import sidebar

def create_layout(df):
    return dmc.MantineProvider(
        children=dbc.Container(
            fluid=True,
            children=[
                dbc.Card(
                    dbc.CardBody(
                        dbc.Tabs(
                            id="method-tabs",
                            active_tab="m1",
                            children=[
                                dbc.Tab(label="Método 1", tab_id="m1"),
                                dbc.Tab(label="Método 2", tab_id="m2"),
                            ],
                        )
                    ),
                    className="mb-3",
                ),
                dbc.Row(
                    [
                        dbc.Col(sidebar(df), xs=12, lg=3),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        dcc.Store(id="sessions-store"),
                                        # Abas removidas. Apenas o Gráfico 2 permanece com altura fixa.
                                        dcc.Graph(id="graph-2", style={"height": "560px"}),
                                    ]
                                )
                            ),
                            xs=12,
                            lg=9,
                        ),
                    ],
                    className="g-3",
                ),
            ],
            className="py-3",
        )
    )