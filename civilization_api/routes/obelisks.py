from flask import Blueprint
from flask import jsonify
from flask import request
import json

obelisks_bp = Blueprint(
    "obelisks",
    __name__
)

@obelisks_bp.route("/api/obelisks")
def get_obelisks():

    with open(
        "datafiles/obelisks.json",
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return jsonify(data)


@obelisks_bp.route("/api/obelisks/<int:id>")
def get_obelisk(id):

    with open(
        "datafiles/obelisks.json",
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    for item in data:

        if item["id"] == id:
            return jsonify(item)

    return jsonify({
        "message": "Obelisk not found"
    }), 404


@obelisks_bp.route("/api/obelisks/search")
def search_obelisks():

    query = request.args.get(
        "q",
        ""
    ).lower()

    with open(
        "datafiles/obelisks.json",
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    result = []

    for item in data:

        if (
            query in item["name"].lower()
            or query in item["arabic_name"]
            or query in item["city"].lower()
        ):
            result.append(item)

    return jsonify(result)