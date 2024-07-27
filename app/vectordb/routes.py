import json
import os

import requests
from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

vectordb = Blueprint("vectordb", __name__)

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from .embedding import *


def dbinit():
    client = QdrantClient(host="localhost", port=6333)
    return client


@vectordb.route("/", methods=["GET"])
def index():
    if not session.get("username") or not session.get("user_id"):
        return redirect("/login")
    return render_template("vector_home.html")


@vectordb.route("/collections/<string:collection_name>", methods=["GET"])
def get_collections(collection_name):
    client = dbinit()
    response = client.scroll(
        collection_name=collection_name,
    )
    return response


@vectordb.route("/collections/<string:collection_name>", methods=["DELETE"])
def delete_collection(collection_name):
    client = dbinit()
    response = client.delete_collection(collection_name=collection_name)
    return response


@vectordb.route("/collections", methods=["POST"])
def create_collections():
    body = request.json
    collection_name = body.get("collection_name")
    vectordim = os.getenv("VECTORDIM", 768)
    if not collection_name:
        return
    client = dbinit()
    response = client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vectordim, distance=Distance.COSINE),
    )
    return response


@vectordb.route("/collections", methods=["PUT"])
def update_collections():
    body = request.json
    collection_name = body.get("collection_name")
    context = body.get("context")
    metadata = body.get("metadata")
    embeded = embed(context)
    points = [PointStruct(id=idx, vector=embeded[idx]) for idx in range(len(embeded))]
    client = dbinit()
    operation_info = client.upsert(
        collection_name=collection_name,
        wait=True,
        points=points,
    )
    return operation_info


@vectordb.route("/search", methods=["POST"])
def search_vectordb():
    body = request.json
    collection_name = body.get("collection_name")
    context = body.get("context")
    metadata = body.get("metadata")
    topk = body.get("topk") or 5
    embeded = embed(context)
    client = dbinit()
    hits = client.search(
        collection_name=collection_name,
        query_vector=embeded,
        limit=topk,  # Return 5 closest points
    )
    return hits
