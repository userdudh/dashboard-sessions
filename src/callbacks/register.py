from src.callbacks.sidebar_callbacks import register_sidebar_callbacks
from src.callbacks.charts_callbacks import register_charts_callbacks


def register_callbacks(app, df):
    register_sidebar_callbacks(app, df)
    register_charts_callbacks(app, df)