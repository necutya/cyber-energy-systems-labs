from flask import Flask

from dash_weather import dash_app, dash_app_1


def create_app():
    server = Flask(__name__, instance_relative_config=True)
    server.config.from_object('config.DefaultConfig')
    
    from app.main.routes import main
    server.register_blueprint(main)
    app = dash_app.create_dash(server)
    app = dash_app_1.create_dash(app)
    return app
