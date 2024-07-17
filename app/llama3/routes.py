import json
import os

import requests
from flask import Blueprint, jsonify, request

chat = Blueprint("chat", __name__)
url = os.getenv("ENDPOINT_LLAMA3", "http://localhost:11434/api/chat")


@chat.route("/chat", methods=["POST"])
def chat_interface():
    if request.method == "POST":
        if request.content_type != "application/json":
            return jsonify({"error": "Unsupported Media Type"}), 415

        data = request.json
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, headers=headers, json=data, stream=True)

        return response.raw

    return jsonify({"error": "Method not allowed"}), 405
