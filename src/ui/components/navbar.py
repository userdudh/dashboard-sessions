import dash_bootstrap_components as dbc
from dash import html

ID_TABS = "tabs-metodos"

def render():

    return html.Div([
        dbc.Nav(
            [
                # Aba 1 (Começa ativa)
                dbc.NavLink("Método 1", href="#", active=True, id="tab-1", n_clicks=0),
                
                # Aba 2
                dbc.NavLink("Método 2", href="#", active=False, id="tab-2", n_clicks=0),
                
                # Aba 3
                dbc.NavLink("Método 3", href="#", active=False, id="tab-3", n_clicks=0),
            ],
            pills=True,     
            fill=True,      
            id=ID_TABS,
            className="gap-2" 
        )
    ], className="mb-4 bg-white p-3 rounded shadow-sm") 