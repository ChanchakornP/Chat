from flask import Flask


def create_app():
    app = Flask(__name__, static_folder="static")

    from .llama3.routes import chat
    from .main.routes import homepage

    app.register_blueprint(homepage)
    app.register_blueprint(chat, url_prefix="/api")

    return app
