import json
import os
import uuid

import requests
from flask import Blueprint, Flask, jsonify, request

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
    user_id = data.get("user_id")
    chat_messages = data.get("chat_messages")

    user = User.query.get(user_id)
    # Error handling
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not chat_messages:
        return jsonify({"error": "Chat Messages not found"}), 404

    for message in chat_messages:
        chat_history = Message(user_id=user_id, chatmessage=message)
        db.session.add(chat_history)

    db.session.commit()
    return jsonify({"message": "Chat History updated"}), 201


@mysql.route("/users/chats", methods=["POST"])
def create_user_chat():
    data = request.json
    user_id = data.get("user_id")
    chat_message = data.get("chat_message")
    conversation_id = data.get("conversation_id")
    sender = data.get("sender")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    if not chat_message:
        return jsonify({"error": "chat_message is required"}), 400

    if not sender:
        return jsonify({"error": "sender is required"}), 400

    if not conversation_id:
        new_conversation = Conversation(user_id=user_id)
        db.session.add(new_conversation)
        db.session.commit()
        conversation_id = new_conversation.id

    else:
        existing_conversation = Conversation.query.filter_by(id=conversation_id).first()
        if not existing_conversation:
            return jsonify({"error": "Conversation ID not found."})

    chat_history = Message(
        conversation_id=conversation_id,
        sender=sender,
        chat_message=chat_message,
    )
    db.session.add(chat_history)
    db.session.commit()

    return (
        jsonify(
            {"message": "Chat History is created", "conversation_id": conversation_id}
        ),
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
