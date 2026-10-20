import json
import sqlite3

conn = sqlite3.connect("database.db")

cursor = conn.cursor()

# ==========================
# Pharaohs
# ==========================

with open(
    "datafiles/pharaohs.json",
    encoding="utf-8"
) as file:

    data = json.load(file)

for item in data:

    cursor.execute("""
    INSERT INTO pharaohs
    VALUES (?,?,?,?,?,?,?,?,?)
    """, (
        item["id"],
        item["name"],
        item["arabic_name"],
        item["dynasty"],
        item["reign"],
        item["capital"],
        item["description"],
        json.dumps(item["achievements"]),
        item["image"]
    ))

print("Pharaohs Imported")


# ==========================
# Statues
# ==========================

with open(
    "datafiles/statues.json",
    encoding="utf-8"
) as file:

    data = json.load(file)

for item in data:

    cursor.execute("""
    INSERT INTO statues
    VALUES (?,?,?,?,?,?,?,?,?)
    """, (
        item["id"],
        item["name"],
        item["arabic_name"],
        item["location"],
        item["period"],
        item["material"],
        item["height_m"],
        item["description"],
        item["image"]
    ))

print("Statues Imported")


# ==========================
# Temples
# ==========================

with open(
    "datafiles/temples.json",
    encoding="utf-8"
) as file:

    data = json.load(file)

for item in data:

    cursor.execute("""
    INSERT INTO temples
    VALUES (?,?,?,?,?,?,?,?,?)
    """, (
        item["id"],
        item["name"],
        item["arabic_name"],
        item["location"],
        item["city"],
        item["built_by"],
        item["period"],
        item["description"],
        item["image"]
    ))

print("Temples Imported")


# ==========================
# Museums
# ==========================

with open(
    "datafiles/museums.json",
    encoding="utf-8"
) as file:

    data = json.load(file)

for item in data:

    cursor.execute("""
    INSERT INTO museums
    VALUES (?,?,?,?,?,?,?,?,?)
    """, (
        item["id"],
        item["name"],
        item["arabic_name"],
        item["city"],
        item["established"],
        item["description"],
        item["image"],
        item["location"]["latitude"],
        item["location"]["longitude"]
    ))

print("Museums Imported")


# ==========================
# Quotes
# ==========================

with open(
    "datafiles/quotes.json",
    encoding="utf-8"
) as file:

    data = json.load(file)

for item in data:

    cursor.execute("""
    INSERT INTO quotes
    VALUES (?,?,?,?)
    """, (
        item["id"],
        item["quote"],
        item["author"],
        item["arabic_author"]
    ))

print("Quotes Imported")


# ==========================
# Obelisks
# ==========================

with open(
    "datafiles/obelisks.json",
    encoding="utf-8"
) as file:

    data = json.load(file)

for item in data:

    cursor.execute("""
    INSERT INTO obelisks
    VALUES (?,?,?,?,?,?,?,?)
    """, (
        item["id"],
        item["name"],
        item["arabic_name"],
        item["city"],
        item["location"],
        item["historical_era"],
        item["builder"],
        json.dumps(item["images"])
    ))

print("Obelisks Imported")

conn.commit()

conn.close()

print("All Data Imported Successfully")