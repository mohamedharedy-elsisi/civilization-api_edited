from flask import Blueprint
from flask import jsonify
from flask import request
import json

statues_bp = Blueprint(
    "statues",
    __name__
)

@statues_bp.route("/api/statues")
def get_statues():

    with open(
        "datafiles/statues.json",
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return jsonify(data)


@statues_bp.route("/api/statues/search")
def search_statues():

    query = request.args.get(
        "q",
        ""
    ).lower()

    with open(
        "datafiles/statues.json",
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    result = []

    for item in data:

        if (
            query in item["name"].lower()
            or query in item["arabic_name"]
            or query in item["location"].lower()
            or query in item["period"].lower()
        ):
            result.append(item)

    return jsonify(result)