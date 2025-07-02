# Tracks and updates system-wide metrics
from pathlib import Path

# Define path for enhanced metrics_v2.py
metrics_v2_path = Path("/mnt/data/metrics.py")

enhanced_metrics_v2_code = '''
import json
from datetime import datetime
from pathlib import Path

# Global live metrics
metrics = {
    "tasks_processed": 0,
    "tasks_failed": 0,
    "agents_generated": 0,
    "clients_onboarded": 0,
    "revenue_generated": 0,
    "client_satisfaction": 0,
    "leads_generated": 0,
    "campaigns_launched": 0,
    "campaign_results": {},  # win/loss per campaign
    "revenue_by_client": {},  # client-specific revenue
    "errors_by_agent": {},
    "performance_by_phase": {},
    "agent_success_fail": {},  # task result tracker
    "forecast": {}  # reserved for AnalystAgent modeling
}

METRICS_FILE = Path(".digi/live_metrics.json")
SNAPSHOT_DIR = Path(".digi/snapshots")
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

def increment_metric(key, amount=1):
    if key in metrics:
        metrics[key] += amount
    elif key == "campaigns_launched":
        metrics[key] = metrics.get(key, 0) + amount
    save_metrics()

def record_agent_error(agent_name):
    metrics["errors_by_agent"][agent_name] = metrics["errors_by_agent"].get(agent_name, 0) + 1
    metrics["tasks_failed"] += 1
    save_metrics()

def record_phase_performance(phase, success=True):
    perf = metrics["performance_by_phase"].setdefault(phase, {"success": 0, "fail": 0})
    if success:
        perf["success"] += 1
    else:
        perf["fail"] += 1
    save_metrics()

def track_agent_task(agent_name, success=True):
    log = metrics["agent_success_fail"].setdefault(agent_name, {"success": 0, "fail": 0})
    if success:
        log["success"] += 1
    else:
        log["fail"] += 1
    save_metrics()

def log_campaign_result(name, result):
    outcomes = metrics["campaign_results"].setdefault(name, {"won": 0, "lost": 0})
    if result == "won":
        outcomes["won"] += 1
    elif result == "lost":
        outcomes["lost"] += 1
    save_metrics()

def add_revenue_for_client(client_id, amount):
    rev = metrics["revenue_by_client"].get(client_id, 0)
    metrics["revenue_by_client"][client_id] = rev + amount
    metrics["revenue_generated"] += amount
    save_metrics()

def update_forecast(model_data):
    metrics["forecast"] = model_data
    save_metrics()

def save_metrics():
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)

def load_metrics():
    global metrics
    if METRICS_FILE.exists():
        with open(METRICS_FILE, "r") as f:
            metrics = json.load(f)

def snapshot_metrics():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(SNAPSHOT_DIR / f"snapshot_{timestamp}.json", "w") as f:
        json.dump(metrics, f, indent=2)

def auto_trigger_responses(client_id):
    if metrics["leads_generated"] < 5:
        from core.digiman_core import update_task_queue
        update_task_queue("Scout Agent", {"task": "Boost lead research", "priority": 3}, client_id)
        update_task_queue("Outreach Agent", {"task": "Revive cold campaigns", "priority": 3}, client_id)
'''

# Save the enhanced metrics_v2.py
metrics_v2_path.write_text(enhanced_metrics_v2_code.strip())

str(metrics_v2_path)
