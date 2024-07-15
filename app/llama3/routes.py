from flask import Blueprint, Flask, jsonify, request

from .llama import llama3

chat = Blueprint("chat", __name__)


@chat.route("/chat", methods=["POST"])
def chat_interface():
    if request.content_type != "application/json":
        return jsonify({"error": "Unsupported Media Type"}), 415

    data = request.json
    question = data.get("chat_completion", "")
    if not question:
        return jsonify({"error": "Please check the APIs document"}), 415

    response = llama3(question)
    return jsonify({"response": response})
