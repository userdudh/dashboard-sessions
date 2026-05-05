import dash
import dash_bootstrap_components as dbc
from src.core.preprocess import get_clean_data 
from src.ui.layout import create_layout
from src.callbacks.register import register_callbacks

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&icon_names=insert_chart"
]

app = dash.Dash(
    __name__, 
    external_stylesheets=external_stylesheets, 
    suppress_callback_exceptions=True
)

server = app.server

df_inicial = get_clean_data(10464, 1)

app.layout = create_layout(df_inicial)

register_callbacks(app, None)

if __name__ == "__main__":
    app.run(debug=True)