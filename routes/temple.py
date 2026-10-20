from flask import Blueprint
from flask import jsonify
from flask import request
import json

temples_bp = Blueprint(
    "temples",
    __name__
)

@temples_bp.route("/api/temples")
def get_temples():

    with open(
        "datafiles/temples.json",
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return jsonify(data)


@temples_bp.route("/api/temples/search")
def search_temples():

    query = request.args.get(
        "q",
        ""
    ).lower()

    with open(
        "datafiles/temples.json",
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
            or query in item["built_by"].lower()
        ):
            result.append(item)

    return jsonify(result)