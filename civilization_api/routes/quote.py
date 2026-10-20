from flask import Blueprint
from flask import jsonify
from flask import request
import json
import random

quotes_bp = Blueprint(
    "quotes",
    __name__
)

@quotes_bp.route("/api/quotes")
def get_quotes():

    with open(
        "datafiles/quotes.json",
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return jsonify(data)


@quotes_bp.route("/api/quotes/random")
def random_quote():

    with open(
        "datafiles/quotes.json",
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return jsonify(
        random.choice(data)
    )


@quotes_bp.route("/api/quotes/search")
def search_quotes():

    query = request.args.get(
        "q",
        ""
    ).lower()

    with open(
        "datafiles/quotes.json",
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    result = []

    for item in data:

        if (
            query in item["quote"].lower()
            or query in item["author"].lower()
            or query in item["arabic_author"]
        ):
            result.append(item)

    return jsonify(result)