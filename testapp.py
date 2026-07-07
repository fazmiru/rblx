from flask import Flask, render_template, jsonify, request
import random

app = Flask(__name__)

spots = [
    {"id": 1, "name": "Riverside Park",  "type": "park",    "lat": 40.7185, "lon": -74.0020, "pct": 18},
    {"id": 2, "name": "Central Beach",   "type": "beach",   "lat": 40.7128, "lon": -74.0160, "pct": 24},
    {"id": 3, "name": "City Gym",        "type": "gym",     "lat": 40.7060, "lon": -73.9980, "pct": 45},
    {"id": 4, "name": "Grand Mall",      "type": "mall",    "lat": 40.7200, "lon": -74.0090, "pct": 82},
    {"id": 5, "name": "Metro Hub",       "type": "transit", "lat": 40.7145, "lon": -74.0060, "pct": 56},
    {"id": 6, "name": "North Park",      "type": "park",    "lat": 40.7230, "lon": -74.0110, "pct": 12},
    {"id": 7, "name": "East Beach",      "type": "beach",   "lat": 40.7090, "lon": -73.9950, "pct": 79},
]

def level(pct):
    return "low" if pct < 35 else ("medium" if pct < 65 else "high")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/spots")
def get_spots():
    filter_type = request.args.get("type", "all")
    result = spots if filter_type == "all" else [s for s in spots if s["type"] == filter_type]
    return jsonify([{**s, "level": level(s["pct"])} for s in result])

@app.route("/api/refresh", methods=["POST"])
def refresh():
    for s in spots:
        s["pct"] = max(5, min(98, s["pct"] + random.randint(-18, 18)))
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)