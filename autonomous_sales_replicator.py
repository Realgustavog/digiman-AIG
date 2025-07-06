import json
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from core.metrics import metrics
from pathlib import Path
from gpt.gpt_router import interpret_command
from datetime import datetime

class AutonomousSalesReplicator:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.metrics = metrics
        self.pricing = self.load_pricing()

    def run_task(self, task):
        log_action("Autonomous Sales Replicator", f"Running task: {task['task']}", self.client_id)

        try:
            gpt_decision = interpret_command(task["task"], self.client_id)
            log_action("Autonomous Sales Replicator", f"GPT decision: {gpt_decision}", self.client_id)
            self.log_reasoning(task["task"], gpt_decision)
            task.update(gpt_decision)
        except Exception as e:
            log_action("Autonomous Sales Replicator", f"GPT failed to interpret: {e}", self.client_id)

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
            log_action("Autonomous Sales Replicator", "Insufficient data to replicate strategy", self.client_id)
            return

        clues = [m["content"] for m in self.memory if "closed deal" in m.get("content", "").lower()]
        if not clues:
            log_action("Autonomous Sales Replicator", "No winning strategy found in memory", self.client_id)
            return

        latest_win = clues[-1]
        summary = f"Replicate strategy: '{latest_win}'"

        update_task_queue("Marketing Agent", {"task": f"Clone campaign: {latest_win}", "priority": 3}, self.client_id)
        update_task_queue("Outreach Agent", {"task": f"Send similar messages to related audience", "priority": 3}, self.client_id)
        update_task_queue("Closer Agent", {"task": f"Use successful closing pitch", "priority": 3}, self.client_id)

        log_action("Autonomous Sales Replicator", f"Strategy cloned:\\n{summary}\\nPricing Context: {self.pricing}", self.client_id)

    def log_reasoning(self, input_text, output_json):
        log_path = Path(f".digi/clients/{self.client_id}/gpt_reasons.log")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as f:
            f.write(f"[{datetime.now()}] INPUT: {input_text}\\nOUTPUT: {output_json}\\n\\n")
