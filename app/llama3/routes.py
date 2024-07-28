import json
import os
import uuid
from datetime import datetime

import requests
from celery import shared_task
from flask import Blueprint, Response, current_app, redirect, request, session, url_for

chat = Blueprint("chat", __name__)
url = os.getenv("ENDPOINT_LLAMA3", "http://localhost:11434/api/chat")
headers = {"Content-Type": "application/json"}


@chat.route("/init", methods=["POST"])
def init_chat():
    body = request.json
    user_prompt = body.get("user_prompt")
    user_id = session.get("user_id")
    chat_id = str(uuid.uuid4())
    create_user_chat_url = current_app.config["BASE_URL"] + url_for(
        "mysql.create_user_chat"
    )
    request_body = {
        "user_id": user_id,
        "message": {
            "conversation_id": chat_id,
            "sender": "user",
            "chat_message": user_prompt,
        },
    }
    init_chat_history_db_response = requests.post(
        create_user_chat_url, json=request_body
    )
    if init_chat_history_db_response.status_code == 201:
        chat_id = init_chat_history_db_response.json().get("conversation_id")
        return redirect(url_for("homepage.index", chat_id=chat_id))


@chat.route("/chat", methods=["POST"])
def chat_interface():
    body = request.json
    user_prompt = body.get("user_prompt")
    chat_id = body.get("chat_id")
    user_id = session.get("user_id")
    chat_history = get_chat_history(chat_id, user_id, user_prompt)
    buffer = []
    update_chat_history_task.delay(chat_id, user_id, user_prompt, sender="user")

    def generate():
        with requests.post(
            url,
            headers=headers,
            json={"model": "llama3", "messages": chat_history},
            stream=True,
        ) as response:
            for chunk in response.iter_lines(decode_unicode=True):
                if chunk:
                    content = json.loads(chunk)["message"]["content"]
                    buffer.append(content)
                    yield content
        update_chat_history_task.delay(chat_id, user_id, buffer, sender="assistant")

    return Response(generate(), content_type="text/plain")


def get_chat_history(chat_id, user_id, user_prompt):
    get_chat_history_url = current_app.config["BASE_URL"] + url_for(
        "mysql.get_user_chat_content", chat_id=chat_id, user_id=user_id
    )
    get_chat_history_response = requests.get(get_chat_history_url)
    if get_chat_history_response == 200:
        messages = get_chat_history_response.json()["chat_messages"]["messages"]
        sorted_messages = sorted(
            messages,
            key=lambda x: datetime.strptime(
                x["created_at"], "%a, %d %b %Y %H:%M:%S GMT"
            ),
        )
        chat_history = [
            {
                "role": (
                    "user"
                    if message["sender"] == "user"
                    else "assistant" if message["sender"] == "assistant" else "system"
                ),
                "content": message["chat_message"],
            }
            for message in sorted_messages
        ]
    else:
        chat_history = []

    chat_history.append({"role": "user", "content": user_prompt})
    return chat_history


@shared_task(name="update_chat_history_task")
def update_chat_history_task(chat_id, user_id, message, sender):
    update_chat_history_url = current_app.url_for("mysql.update_user_chat")
    body = {
        "chat_id": chat_id,
        "chat_message": "".join(message),
        "sender": sender,
    }
    response = requests.put(url=update_chat_history_url, json=body)
    response.raise_for_status()
