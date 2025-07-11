from pathlib import Path
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
import re
import inspect

# === Load Environment + Ensure .digi Directory Exists ===
load_dotenv()
CONFIG_FILE = Path(".digi/config.json")
CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

# === Logging Setup ===
logger = logging.getLogger("DigiManCore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

# === Global Metrics ===
metrics = {
    "tasks_processed": 0,
    "tasks_failed": 0,
    "agents_generated": 0,
    "clients_onboarded": 0,
    "revenue_generated": 0,
    "client_satisfaction": 0,
    "leads_generated": 0
}

# === Logging Utility ===
def log_action(agent_name, action, client_id=None):
    log_dir = Path(f".digi/clients/{client_id}") if client_id else Path(".digi")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "actions.log"
    try:
        with log_path.open("a") as f:
            f.write(f"[{datetime.now()}] {agent_name}: {action}\n")
    except Exception as e:
        logger.error(f"Failed to log action for {agent_name}: {e}")
    logger.info(f"{agent_name}: {action}")
    metrics["tasks_processed"] += 1

# === Sandbox Mode Integration ===
SANDBOX_MODE = os.getenv("SANDBOX_MODE", "False").lower() == "true"

def sandbox_log(agent_name, action, client_id=None):
    if SANDBOX_MODE:
        log_action(agent_name, f"[SANDBOX MODE] {action}", client_id)

# === Load Config ===
def load_config():
    config = {}
    for key, value in os.environ.items():
        if any(s in key for s in ['_KEY', '_TOKEN', '_ACCOUNT', '_SERVER', '_PORT']):
            config[key] = value

    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open("r") as f:
                file_config = json.load(f)
            config.update(file_config)
        except Exception as e:
            log_action("DigiManCore", f"Failed to load config: {e}")

    try:
        with CONFIG_FILE.open("w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        log_action("DigiManCore", f"Failed to save config: {e}")

    return config

CONFIG = load_config()

# === Task Queue Utilities ===
def load_task_queue(client_id=None):
    log_dir = Path(f".digi/clients/{client_id}") if client_id else Path(".digi")
    path = log_dir / "agent_queue.json"
    if path.exists():
        try:
            with path.open("r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def update_task_queue(agent_name, task, client_id=None):
    log_dir = Path(f".digi/clients/{client_id}") if client_id else Path(".digi")
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / "agent_queue.json"
    queue = load_task_queue(client_id)
    task_entry = {
        "task": task,
        "priority": task.get("priority", 1),
        "timestamp": str(datetime.now())
    }
    queue.setdefault(agent_name, []).append(task_entry)
    try:
        with path.open("w") as f:
            json.dump(queue, f, indent=2)
        log_action(agent_name, f"Queued task: {task}", client_id)
    except Exception as e:
        logger.error(f"Failed to update task queue for {agent_name}: {e}")

# === Agent Quality Score ===
def evaluate_agent_quality(code):
    score = 0
    reasons = []
    try:
        compile(code, "<string>", "exec")
        score += 1
    except SyntaxError as e:
        reasons.append(f"Syntax error: {e}")
    if re.search(r"class \w+\s*(\(|:)", code):
        score += 1
    else:
        reasons.append("Missing class definition")
    if len(re.findall(r"def ", code)) >= 3:
        score += 1
    else:
        reasons.append("Less than 3 methods defined")
    if "log_action" in code:
        score += 1
    else:
        reasons.append("Missing log_action usage")
    return score, reasons
