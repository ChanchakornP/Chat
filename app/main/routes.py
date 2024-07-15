from flask import Blueprint, render_template, url_for
from markupsafe import Markup

homepage = Blueprint(
    "homepage", __name__, template_folder="templates", static_folder="static"
)


@homepage.route("/")
def index():
    endpoint_chat = url_for("chat.chat_interface")
    return Markup(render_template("home.html", endpoint_chat=endpoint_chat))
