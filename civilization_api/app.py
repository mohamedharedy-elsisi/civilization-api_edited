from flask import Flask

from routes.pharaoh import pharaohs_bp
from routes.statue import statues_bp
from routes.temple import temples_bp
from routes.museum import museums_bp
from routes.quote import quotes_bp
from routes.obelisks import obelisks_bp

app = Flask(__name__)

# ==========================
# Register Blueprints
# ==========================

app.register_blueprint(pharaohs_bp)
app.register_blueprint(statues_bp)
app.register_blueprint(temples_bp)
app.register_blueprint(museums_bp)
app.register_blueprint(quotes_bp)
app.register_blueprint(obelisks_bp)

# ==========================
# Home Route
# ==========================

@app.route("/")
def home():
    return {
        "message": "Civilization API is running"
    }

# ==========================
# Run App
# ==========================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )