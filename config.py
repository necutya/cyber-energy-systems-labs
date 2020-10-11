import os


class DefaultConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY').encode()
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')


class ProductionConfig(DefaultConfig):
    DEBUG = False
