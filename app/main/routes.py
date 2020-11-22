from flask import render_template, redirect, Blueprint

from dash_weather import (
    dash_weather,
    dash_weather_mode,
    dash_rose,
    dash_wind_durations,
    dash_sunn,
    dash_sunn_activeness
)
main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    return render_template("home.html")


@main.route('/weather')
def weather():
    return render_template(
        "weather.html",
        dash_weather_url=dash_weather.url_base,
        dash_weather_mode_url=dash_weather_mode.url_base,
        dash_rose_url=dash_rose.url_base,
        dash_wind_url=dash_wind_durations.url_base,
        dash_sunn_url=dash_sunn.url_base,
        dash_sunn_activeness_url=dash_sunn_activeness.url_base,
    )

