import dash
import dash_bootstrap_components as dbc

from src.core.load import data_loader
from src.core.preprocess import preprocess
from src.ui.layout import create_layout
from src.callbacks.register import register_callbacks

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

df = preprocess(data_loader())

app.layout = create_layout(df)
register_callbacks(app, df)

if __name__ == "__main__":
    app.run(debug=True)