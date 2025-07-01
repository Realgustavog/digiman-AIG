# Logic for Autonomous Sales Replicator
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from core.metrics import metrics

class AutonomousSalesReplicator:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.metrics = metrics

    def run_task(self, task):
        log_action("Autonomous Sales Replicator", f"Running task: {task['task']}", self.client_id)
        if "replicate" in task["task"].lower():
            self.replicate_successful_strategy()

    def replicate_successful_strategy(self):
        leads = self.metrics.get("leads_generated", 0)
        revenue = self.metrics.get("revenue_generated", 0)
        clients = self.metrics.get("clients_onboarded", 0)

        if leads < 10 or revenue < 1000:
            log_action("Autonomous Sales Replicator", "Insufficient data to replicate strategy", self.client_id)
            return

        high_performance_clues = []
        for m in self.memory:
            if "closed deal" in m.get("content", "").lower():
                high_performance_clues.append(m["content"])

        if not high_performance_clues:
            log_action("Autonomous Sales Replicator", "No high-conversion patterns found", self.client_id)
            return

        summary = f"Replicate strategy: Use high-performing approach from: '{high_performance_clues[-1]}'"
        update_task_queue("Marketing Agent", {"task": f"Create campaign based on winning strategy", "priority": 3}, self.client_id)
        update_task_queue("Outreach Agent", {"task": f"Launch outbound to similar audience", "priority": 3}, self.client_id)
        update_task_queue("Closer Agent", {"task": f"Use successful pitch approach", "priority": 3}, self.client_id)

        log_action("Autonomous Sales Replicator", f"Strategy cloned and queued to agents. Summary: {summary}", self.client_id)
