from flask import Blueprint
from flask import jsonify
from flask import request
import json

museums_bp = Blueprint(
    "museums",
    __name__
)

@museums_bp.route("/api/museums")
def get_museums():

    with open(
        "datafiles/museums.json",
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return jsonify(data)


@museums_bp.route("/api/museums/search")
def search_museums():

    query = request.args.get(
        "q",
        ""
    ).lower()

    with open(
        "datafiles/museums.json",
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