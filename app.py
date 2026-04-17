import dash
import dash_bootstrap_components as dbc
from src.core.load import data_loader
from src.core.preprocess import preprocess
from src.ui.layout import create_layout
from src.callbacks.register import register_callbacks

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

# Carrega curso padrão 10464 no início
df_inicial = preprocess(data_loader(10464, 1))

# O layout chama create_layout (que já contém o filters-store internamente)
app.layout = create_layout(df_inicial)

register_callbacks(app, None)

if __name__ == "__main__":
    app.run(debug=False)