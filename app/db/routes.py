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
    chat_id = data.get("chat_id")
    chat_message = data.get("chat_message")
    sender = data.get("sender")
    # if not chat_id:
    #     return jsonify({"error": "Chat ID not found"}), 404
    # if not chat_message:
    #     return jsonify({"error": "Messages not found"}), 404
    # if sender not in ["user", "assistant", "system"]:
    #     return jsonify({"error": "Sender is not correct"}), 404

    conversation = Conversation.query.get(chat_id)
    if not conversation:
        return jsonify({"error": "Conversation not found"}), 404

    message = Message(
        conversation_id=chat_id,  # Associate message with the conversation
        sender=sender,
        chat_message=chat_message,
    )
    db.session.add(message)
    db.session.commit()
    return jsonify({"message": "Chat History updated"}), 201


@mysql.route("/users/chats", methods=["POST"])
def create_user_chat():
    data = request.json
    user_id = data.get("user_id")
    message_raw = data.get("message")
    user = User.query.filter_by(id=user_id).first()
    # Error handling
    if not user:
        return jsonify({"error": "User not found"}), 404
    # if not message_raw:
    #     return jsonify({"error": "Messages not found"}), 404
    chat_id = str(uuid.uuid4())

    if isinstance(message_raw, dict):
        message = [
            Message(
                conversation_id=message_raw.get("conversation_id"),
                sender=message_raw.get("sender"),
                chat_message=message_raw.get("chat_message"),
            )
        ]
    elif isinstance(message_raw, list):
        message = [
            Message(
                conversation_id=message_raw_.get("conversation_id"),
                sender=message_raw_.get("sender"),
                chat_message=message_raw_.get("chat_message"),
            )
            for message_raw_ in message_raw
        ]
    else:
        message = []
    new_conversation = Conversation(id=chat_id, user_id=user_id, message=message)
    db.session.add(new_conversation)
    db.session.commit()
    return (
        jsonify({"message": "Chat History is created", "conversation_id": chat_id}),
        201,
    )


@mysql.route("/users/<string:user_id>", methods=["GET"])
def get_user_chat_id(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    chat_histories = (
        Conversation.query.with_entities(Conversation.id)
        .filter_by(user_id=user_id)
        .all()
    )
    chat_ids = [id for id, in chat_histories]

    return jsonify({"user_id": user_id, "chat_ids": chat_ids})


@mysql.route("/users/<string:user_id>/chats/<string:chat_id>", methods=["GET"])
def get_user_chat_content(user_id, chat_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    chat_histories = Conversation.query.filter_by(user_id=user_id, id=chat_id).first()
    if not chat_histories:
        return jsonify({"error": "Chat message not found"}), 404

    chat_messages = {
        "id": chat_histories.id,
        "messages": [
            {
                "id": message.id,
                "sender": message.sender,
                "chat_message": message.chat_message,
                "created_at": message.created_at,
            }
            for message in sorted(
                chat_histories.message, key=lambda msg: msg.created_at
            )
        ],
        "created_at": chat_histories.created_at,
    }
    return jsonify({"user_id": user_id, "chat_messages": chat_messages})


@mysql.route("/users/chats/<string:chat_id>", methods=["DELETE"])
def delete_user_chat(chat_id):
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    chat_history = Conversation.query.filter_by(id=chat_id, user_id=user_id).first()
    if not chat_history:
        return (
            jsonify({"error": "Chat message not found or does not belong to the user"}),
            404,
        )
    messages = Message.query.filter_by(conversation_id=chat_id).all()
    for message in messages:
        db.session.delete(message)

    db.session.delete(chat_history)
    db.session.commit()

    return jsonify({"message": "Chat message deleted"}), 200
