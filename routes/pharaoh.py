from flask import Blueprint
from flask import jsonify
from flask import request
import json

pharaohs_bp = Blueprint(
    "pharaohs",
    __name__
)

@pharaohs_bp.route("/api/pharaohs")
def get_pharaohs():

    with open(
        "datafiles/pharaohs.json",
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return jsonify(data)


@pharaohs_bp.route("/api/pharaohs/search")
def search_pharaohs():

    query = request.args.get(
        "q",
        ""
    ).lower()

    with open(
        "datafiles/pharaohs.json",
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    result = []

    for item in data:

        if (
            query in item["name"].lower()
            or query in item["arabic_name"]
            or query in item["dynasty"].lower()
            or query in item["capital"].lower()
        ):
            result.append(item)

    return jsonify(result)