# Logic for Autonomous Sales Replicator
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from core.metrics import metrics
from pathlib import Path
import json

class AutonomousSalesReplicator:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.metrics = metrics
        self.pricing = self.load_pricing()

    def run_task(self, task):
        log_action("Autonomous Sales Replicator", f"Running task: {task['task']}", self.client_id)
        if "replicate" in task["task"].lower():
            self.replicate_successful_strategy()

    def load_pricing(self):
        path = Path("pricing.json")
        if path.exists():
            return json.loads(path.read_text())
        return {}

    def replicate_successful_strategy(self):
        leads = self.metrics.get("leads_generated", 0)
        revenue = self.metrics.get("revenue_generated", 0)
        clients = self.metrics.get("clients_onboarded", 0)

        if leads < 10 or revenue < 1000:
            log_action("Autonomous Sales Replicator", "Not enough data to replicate. Generate more leads first.", self.client_id)
            return

        clues = [m["content"] for m in self.memory if "closed deal" in m.get("content", "").lower()]
        if not clues:
            log_action("Autonomous Sales Replicator", "No closed deal history to replicate from.", self.client_id)
            return

        latest_win = clues[-1]
        summary = f"Replicate winning move: '{latest_win}'"

        # Queue tasks to replicate strategy across agents
        update_task_queue("Marketing Agent", {"task": f"Replicate: {latest_win}", "priority": 3}, self.client_id)
        update_task_queue("Outreach Agent", {"task": f"Target similar audience using: {latest_win}", "priority": 3}, self.client_id)
        update_task_queue("Closer Agent", {"task": f"Use proven pitch: {latest_win}", "priority": 3}, self.client_id)

        log_action("Autonomous Sales Replicator", f"Strategy cloned and deployed.\nPricing awareness: {self.pricing}", self.client_id)
