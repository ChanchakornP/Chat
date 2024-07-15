from flask import Blueprint, render_template, url_for
from markupsafe import Markup

homepage = Blueprint(
    "homepage", __name__, template_folder="templates", static_folder="static"
)


@homepage.route("/")
def index():
    return Markup(render_template("home.html"))
