import os

basedir = os.path.abspath(os.path.dirname(__file__))

class DefaultConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY').encode()
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, 'app.db')


class ProductionConfig(DefaultConfig):
    DEBUG = False
