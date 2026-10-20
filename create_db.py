import sqlite3

conn = sqlite3.connect("database.db")

cursor = conn.cursor()

# ==========================
# Pharaohs
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS pharaohs(
    id INTEGER PRIMARY KEY,
    name TEXT,
    arabic_name TEXT,
    dynasty TEXT,
    reign TEXT,
    capital TEXT,
    description TEXT,
    achievements TEXT,
    image TEXT
)
""")

# ==========================
# Statues
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS statues(
    id INTEGER PRIMARY KEY,
    name TEXT,
    arabic_name TEXT,
    location TEXT,
    period TEXT,
    material TEXT,
    height_m REAL,
    description TEXT,
    image TEXT
)
""")

# ==========================
# Temples
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS temples(
    id INTEGER PRIMARY KEY,
    name TEXT,
    arabic_name TEXT,
    location TEXT,
    city TEXT,
    built_by TEXT,
    period TEXT,
    description TEXT,
    image TEXT
)
""")

# ==========================
# Museums
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS museums(
    id INTEGER PRIMARY KEY,
    name TEXT,
    arabic_name TEXT,
    city TEXT,
    established INTEGER,
    description TEXT,
    image TEXT,
    latitude REAL,
    longitude REAL
)
""")

# ==========================
# Quotes
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS quotes(
    id INTEGER PRIMARY KEY,
    quote TEXT,
    author TEXT,
    arabic_author TEXT
)
""")

# ==========================
# Obelisks
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS obelisks(
    id INTEGER PRIMARY KEY,
    name TEXT,
    arabic_name TEXT,
    city TEXT,
    location TEXT,
    historical_era TEXT,           
    builder TEXT,
    description TEXT,
    images TEXT
)
""")

conn.commit()

conn.close()

print("Database Created Successfully")