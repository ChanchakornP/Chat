import os

from celery import Celery, Task
from config import DevelopmentConfig
from db.models import db
from flask import Flask

from flask_session import Session


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def create_app():
    app = Flask(__name__, static_folder="static")

    from db.routes import mysql
    from llama3.routes import chat
    from main.routes import homepage
    from vectordb.routes import vectordb

    app.config.from_object(DevelopmentConfig)
    db.init_app(app)

    app.register_blueprint(homepage)
    app.register_blueprint(chat, url_prefix="/api")
    app.register_blueprint(mysql, url_prefix="/db")
    app.register_blueprint(vectordb, url_prefix="/vectordb")

    with app.app_context():
        db.create_all()
    Session(app)
    app.config.from_mapping(
        CELERY=dict(
            broker_url=os.getenv("REDIS_URL", "redis://localhost"),
            result_backend=os.getenv("REDIS_URL", "redis://localhost"),
            task_ignore_result=True,
        ),
    )
    celery_init_app(app)

    return app
