from flask import render_template, redirect, Blueprint

from dash_weather import dash_app as dash_weather_app
from dash_weather import dash_app_1 as dash_weather_app_test

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    return render_template("home.html")


@main.route('/weather')
def weather():
    return render_template(
        "weather.html",
        dash_weather_url=dash_weather_app.url_base,
        dash_weather_test=dash_weather_app_test.url_base,
    )

