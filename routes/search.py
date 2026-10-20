from flask import Blueprint, request, jsonify
import json

search_bp = Blueprint(
    "search",
    __name__
)

@search_bp.route(
    "/api/search"
)
def search():

    query = request.args.get(
        "q",
        ""
    ).lower()

    results = []

    files = [

        "datafiles/pharaohs.json",
        "datafiles/statues.json",
        "datafiles/temples.json",
        "datafiles/museums.json",
        "datafiles/obelisks.json",
        "datafiles/pyramids.json",

    ]

    for file_name in files:

        with open(
            file_name,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        for item in data:

            if (

                query in item.get(
                    "name",
                    ""
                ).lower()

                or

                query in item.get(
                    "arabic_name",
                    ""
                ).lower()

            ):

                results.append(item)

    return jsonify(results)