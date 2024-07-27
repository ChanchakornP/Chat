import os

from flask import Flask
from flask_session import Session

from .config import DevelopmentConfig
from .db.models import db


def create_app():
    app = Flask(__name__, static_folder="static")

    from .db.routes import mysql
    from .llama3.routes import chat
    from .main.routes import homepage
    from .vectordb.routes import vectordb

    app.config.from_object(DevelopmentConfig)
    db.init_app(app)

    app.register_blueprint(homepage)
    app.register_blueprint(chat, url_prefix="/api")
    app.register_blueprint(mysql, url_prefix="/db")
    app.register_blueprint(vectordb, url_prefix="/vectordb")

    with app.app_context():
        db.create_all()
    Session(app)
    return app
