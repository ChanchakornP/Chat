import os

import requests
from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from markupsafe import Markup

homepage = Blueprint(
    "homepage", __name__, template_folder="templates", static_folder="static"
)

REGISTRANT = {}


@homepage.route("/c/<string:chat_id>", methods=["GET"])
@homepage.route("/", methods=["GET"], defaults={"chat_id": None})
def index(chat_id):
    if not session.get("username") or not session.get("user_id"):
        return redirect("/login")
    get_chat_ids_url = current_app.config["BASE_URL"] + url_for(
        "mysql.get_user_chat_id", user_id=session.get("user_id")
    )
    chat_message = {}
    response = requests.get(get_chat_ids_url)
    chat_ids = response.json().get("chat_ids")
    if chat_id:
        get_chat_content_url = current_app.config["BASE_URL"] + url_for(
            "mysql.get_user_chat_content",
            user_id=session.get("user_id"),
            chat_id=chat_id,
        )
        response_chat_content = requests.get(get_chat_content_url)
        chat_message = response_chat_content.json().get("chat_messages")
        if response_chat_content.status_code == 404:
            return redirect("/")
    return render_template("home.html", chat_message=chat_message, chat_ids=chat_ids)


@homepage.route("/login", methods=["GET", "POST"])
def login():
    if session.get("username"):
        return redirect("/")
    if request.method == "POST":
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return jsonify({"error": "Please provide username and password"}), 405
        verify_url = current_app.config["BASE_URL"] + url_for("mysql.verify_user")
        response = requests.post(
            verify_url, json={"username": username, "password": password}
        )
        if response.status_code == 200:
            session["username"] = username
            session["user_id"] = response.json().get("user_id")
            return redirect(url_for("homepage.index"))
        else:
            return (
                jsonify({"error": "Failed to login. Please try again."}),
                response.status_code,
            )
    return render_template("login.html")


@homepage.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("homepage.login"))


@homepage.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        create_user_url = current_app.config["BASE_URL"] + url_for("mysql.create_user")
        response = requests.post(
            create_user_url, json={"username": username, "password": password}
        )
        if response.status_code == 201:
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("homepage.login"))
        else:
            return jsonify({"error": "Failed to create user"}), response.status_code
    elif request.method == "GET":
        return render_template("register.html")


@homepage.route("/test")
def test():
    return render_template("test.html")
