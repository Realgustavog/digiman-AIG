from pathlib import Path

# Define full enhanced digiman_server.py
digiman_server_path = Path("/mnt/data/digiman_server.py")

digiman_server_code = '''
from flask import Flask, request, jsonify
from core.digiman_core import metrics, update_task_queue, log_action
from gpt.gpt_router import interpret_command
from core.memory_store import load_memory
import logging

app = Flask(__name__)
logger = logging.getLogger("DigiManAPI")

@app.route("/digiman/command", methods=["POST"])
def command():
    data = request.json
    client_id = data.get("client_id", "default")
    input_text = data.get("message", "")

    gpt_task = interpret_command(input_text, client_id)
    update_task_queue(gpt_task["agent"], gpt_task, client_id)
    log_action("DigiManAPI", f"Delegated to {gpt_task['agent']}: {gpt_task['task']}", client_id)

    return jsonify({
        "status": "received",
        "task": gpt_task
    })

@app.route("/digiman/insights", methods=["GET"])
def insights():
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
'''

# Save the updated API file
digiman_server_path.write_text(digiman_server_code.strip())

str(digiman_server_path)
