from flask import Flask
import pandas as pd

from dash_weather import (
    dash_weather,
    dash_weather_mode,
    dash_rose,
    dash_wind_durations,
    dash_sunn,
    dash_sunn_activeness
)


def create_app():
    server = Flask(__name__, instance_relative_config=True)
    server.config.from_object('config.DefaultConfig')
    
    from app.main.routes import main
    server.register_blueprint(main)

    # df = pd.read_excel('data.xlsx')
    # df_sun = pd.read_excel('solyara.xlsx')
    df = pd.read_excel('data_test.xlsx')
    df_sun = pd.read_excel('data_test.xlsx')


    # first part
    app = dash_weather.create_dash(server, df)
    app = dash_weather_mode.create_dash(app, df)
    app = dash_rose.create_dash(app, df)
    app = dash_wind_durations.create_dash(app, df)
    app = dash_sunn.create_dash(app, df_sun)
    app = dash_sunn_activeness.create_dash(app, df_sun)

    return app
