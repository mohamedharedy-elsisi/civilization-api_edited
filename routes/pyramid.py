from flask import Blueprint
from flask import jsonify
from flask import request
import json

pyramids_bp = Blueprint(
    "pyramids",
    __name__
)


@pyramids_bp.route("/api/pyramids")
def get_pyramids():

    with open(
        "datafiles/pyramids.json",
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return jsonify(data)


@pyramids_bp.route("/api/pyramids/<int:id>")
def get_pyramid(id):

    with open(
        "datafiles/pyramids.json",
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    for item in data:

        if item["id"] == id:
            return jsonify(item)

    return jsonify({
        "message": "Pyramid not found"
    }), 404


@pyramids_bp.route("/api/pyramids/search")
def search_pyramids():

    query = request.args.get(
        "q",
        ""
    ).lower()

    with open(
        "datafiles/pyramids.json",
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    result = []

    for item in data:

        if (
            query in item["name"].lower()
            or query in item["arabic_name"].lower()
            or query in item["location"].lower()
            or query in item["city"].lower()
            or query in item["built_by"].lower()
        ):
            result.append(item)

    return jsonify(result)