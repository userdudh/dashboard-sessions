import dash
import dash_bootstrap_components as dbc

from src.core.preprocess import get_clean_data
from src.ui.layout import create_layout
from src.callbacks.register import register_callbacks


external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined",
]

external_scripts = [
    "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.11.13/dayjs.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.11.13/plugin/customParseFormat.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.11.13/locale/pt-br.min.js",
]


app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    external_scripts=external_scripts,
    suppress_callback_exceptions=True,
)

server = app.server

df_inicial = get_clean_data(10464, 1)

app.layout = create_layout(df_inicial)

register_callbacks(app, None)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)