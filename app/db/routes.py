import json
import os
import uuid

import requests
from flask import Blueprint, Flask, jsonify, request

from .models import ChatHistory, User, db

mysql = Blueprint("mysql", __name__)


@mysql.route("/users/verify", methods=["POST"])
def verify_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    authen_result = User.query.filter_by(username=username, password=password).first()
    if not authen_result:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "User verified"}), 200


@mysql.route("/users/create", methods=["POST"])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Name is required"}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created", "user_id": new_user.id}), 201


@mysql.route("/users/chats", methods=["PUT"])
def update_user_chat():
    data = request.json
    user_id = data.get("user_id")
    chat_messages = data.get("chat_messages")

    user = User.query.get(user_id)
    # Error handling
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not chat_messages:
        return jsonify({"error": "Chat Messages not found"}), 404

    for message in chat_messages:
        chat_history = ChatHistory(user_id=user_id, chatmessage=message)
        db.session.add(chat_history)

    db.session.commit()
    return jsonify({"message": "Chat History updated"}), 201


@mysql.route("/users/chats", methods=["POST"])
def create_user_chat():
    data = request.json
    user_id = data.get("user_id")
    chat_message = data.get("chat_message")
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    if not chat_message:
        return jsonify({"error": "Chat message is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    chat_id = str(uuid.uuid4())

    chat_history = ChatHistory(id=chat_id, user_id=user_id, chatmessage=chat_message)
    db.session.add(chat_history)
    db.session.commit()

    return jsonify({"message": "Chat History is created"}), 201


@mysql.route("/users/<string:user_id>/chats/<string:chat_id>", methods=["GET"])
@mysql.route("/users/<string:user_id>/chats", methods=["GET"])
def get_user_chat(user_id, chat_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if chat_id is None:
        # Return all chat messages for the user
        chat_histories = ChatHistory.query.filter_by(user_id=user_id).all()
        chat_messages = [
            {
                "id": chat.id,
                "message": chat.chatmessage,
                "create_date": chat.create_date,
            }
            for chat in chat_histories
        ]
        return jsonify({"user_id": user_id, "chat_messages": chat_messages})

    else:
        # Return a specific message
        chat_history = ChatHistory.query.filter_by(user_id=user_id, id=chat_id).first()
        if not chat_history:
            return jsonify({"error": "Chat message not found"}), 404

        return jsonify(
            {
                "user_id": user_id,
                "chat_message": {
                    "id": chat_history.id,
                    "message": chat_history.chatmessage,
                    "create_date": chat_history.create_date,
                },
            }
        )


@mysql.route("/users/<string:user_id>/chats/<string:chat_id>", methods=["DELETE"])
def delete_user_chat(user_id, chat_id):
    # Validate user_id and chat_id parameters
    chat_history = ChatHistory.query.filter_by(id=chat_id, user_id=user_id).first()

    if not chat_history:
        return (
            jsonify({"error": "Chat message not found or does not belong to the user"}),
            404,
        )

    db.session.delete(chat_history)
    db.session.commit()

    return jsonify({"message": "Chat message deleted"}), 200
