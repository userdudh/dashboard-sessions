import dash
import dash_bootstrap_components as dbc

from src.core.load import data_loader
from src.core.preprocess import preprocess
from src.ui.layout import create_layout
from src.callbacks.register import register_callbacks

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

dfs = {
    "m1": preprocess(data_loader(1)),
    "m2": preprocess(data_loader(2)),
    "m3": preprocess(data_loader(3))
}

app.layout = create_layout(dfs["m1"])
register_callbacks(app, dfs)

if __name__ == "__main__":
    app.run()