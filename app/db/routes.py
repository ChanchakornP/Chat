import json
import os
import uuid

import requests
from flask import Blueprint, Flask, jsonify, request, session

from .models import Conversation, Message, User, db

mysql = Blueprint("mysql", __name__)


@mysql.route("/users/verify", methods=["POST"])
def verify_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    authen_result = User.query.filter_by(username=username, password=password).first()
    if not authen_result:
        return jsonify({"error": "User not found"}), 404
    user_id = authen_result.id

    return jsonify({"message": "User verified", "user_id": user_id}), 200


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
    user_id = session.get("user_id")
    chat_id = data.get("chat_id")
    message_raw = data.get("message")

    user = User.query.filter_by(id=user_id).first()
    # Error handling
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not chat_id:
        return jsonify({"error": "Chat ID not found"}), 404
    if not message_raw:
        return jsonify({"error": "Messages not found"}), 404

    conversation = Conversation.query.get(chat_id)
    if not conversation:
        return jsonify({"error": "Conversation not found"}), 404

    for msg in message_raw:
        message = Message(
            conversation_id=chat_id,  # Associate message with the conversation
            sender=msg.get("role"),
            chat_message=msg.get("content"),
        )
        db.session.add(message)
    db.session.commit()
    return jsonify({"message": "Chat History updated"}), 201


@mysql.route("/users/chats", methods=["POST"])
def create_user_chat():
    data = request.json
    user_id = session.get("user_id")
    message_raw = data.get("message")

    user = User.query.filter_by(id=user_id).first()
    # Error handling
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not message_raw:
        return jsonify({"error": "Messages not found"}), 404
    chat_id = str(uuid.uuid4())
    message = []
    for msg in message_raw:
        message.append(
            Message(
                conversation_id=chat_id,  # Associate message with the conversation
                sender=msg.get("role"),
                chat_message=msg.get("content"),
            )
        )

    new_conversation = Conversation(id=chat_id, user_id=user_id, message=message)
    db.session.add(new_conversation)
    db.session.commit()
    return (
        jsonify({"message": "Chat History is created", "conversation_id": chat_id}),
        201,
    )


@mysql.route("/users/<string:user_id>/chats/<string:chat_id>", methods=["GET"])
@mysql.route(
    "/users/<string:user_id>/chats", methods=["GET"], defaults={"chat_id": None}
)
def get_user_chat(user_id, chat_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if chat_id is None:
        # Return all chat messages for the user
        chat_histories = Conversation.query.filter_by(user_id=user_id).all()
    else:
        chat_histories = [
            Conversation.query.filter_by(user_id=user_id, id=chat_id).first()
        ]
        if not chat_histories:
            return jsonify({"error": "Chat message not found"}), 404

    chat_messages = [
        {
            "id": conversation.id,
            "messages": [
                {
                    "id": message.id,
                    "sender": message.sender,
                    "chat_message": message.chat_message,
                    "created_at": message.created_at,
                }
                for message in conversation.message
            ],
            "created_at": conversation.created_at,
        }
        for conversation in chat_histories
    ]
    return jsonify({"user_id": user_id, "chat_messages": chat_messages})


@mysql.route("/users/<string:user_id>/chats/<string:chat_id>", methods=["DELETE"])
def delete_user_chat(user_id, chat_id):
    # Validate user_id and chat_id parameters
    chat_history = Message.query.filter_by(id=chat_id, user_id=user_id).first()

    if not chat_history:
        return (
            jsonify({"error": "Chat message not found or does not belong to the user"}),
            404,
        )

    db.session.delete(chat_history)
    db.session.commit()

    return jsonify({"message": "Chat message deleted"}), 200
