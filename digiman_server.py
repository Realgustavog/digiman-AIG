from pathlib import Path
from flask import Flask, request, jsonify
from core.digiman_core import metrics, update_task_queue, log_action
from gpt.gpt_router import interpret_command
from core.memory_store import load_memory
import logging
import os

app = Flask(__name__)
logger = logging.getLogger("DigiManAPI")
logging.basicConfig(level=logging.INFO)

# Optional API key security
API_KEY = os.getenv("DIGIMAN_API_KEY", "open-access")

def validate_request(req):
    key = req.headers.get("Authorization", "")
    return key == f"Bearer {API_KEY}"

@app.route("/digiman/command", methods=["POST"])
def command():
    if not validate_request(request):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    data = request.json or {}
    client_id = data.get("client_id", "default")
    input_text = data.get("message", "")

    if not input_text:
        return jsonify({"status": "error", "message": "Missing message"}), 400

    try:
        gpt_task = interpret_command(input_text, client_id)
        update_task_queue(gpt_task["agent"], gpt_task, client_id)
        log_action("DigiManAPI", f"Delegated to {gpt_task['agent']}: {gpt_task['task']}", client_id)

        return jsonify({
            "status": "received",
            "task": gpt_task
        })
    except Exception as e:
        logger.error(f"Command processing failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/digiman/insights", methods=["GET"])
def insights():
    if not validate_request(request):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    client_id = request.args.get("client_id", "default")
    memory = load_memory(client_id)
    return jsonify({
        "status": "success",
        "metrics": metrics,
        "recent_memory": memory[-5:]
    })

@app.route("/digiman/ping", methods=["GET"])
def ping():
    return jsonify({"status": "alive", "message": "DigiMan API is running"})

@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "message": "Route not found"}), 404
'''

# Save the secure enhanced API file
secure_digiman_server_path.write_text(secure_server_code.strip())

str(secure_digiman_server_path)
