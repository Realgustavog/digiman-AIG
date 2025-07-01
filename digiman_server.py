
from flask import Flask, request, jsonify
from core.digiman_core import metrics
import logging

app = Flask(__name__)
logger = logging.getLogger("DigiManAPI")

@app.route("/digiman/command", methods=["POST"])
def command():
    data = request.json
    logger.info(f"Received command: {data}")
    return jsonify({"status": "received", "message": data})

@app.route("/digiman/insights", methods=["GET"])
def insights():
    return jsonify({
        "status": "success",
        "metrics": metrics
    })
