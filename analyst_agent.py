import json
from core.metrics import metrics
from core.memory_store import load_memory
from core.digiman_core import log_action, update_task_queue
from pathlib import Path
from gpt.gpt_router import interpret_command
from datetime import datetime

class AnalystAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.metrics = metrics
        self.pricing = self.load_pricing()

    def run_task(self, task):
        log_action("Analyst Agent", f"Running task: {task['task']}", self.client_id)

        try:
            gpt_decision = interpret_command(task["task"], self.client_id)
            log_action("Analyst Agent", f"GPT Decision: {gpt_decision}", self.client_id)
            self.log_reasoning(task["task"], gpt_decision)
            task.update(gpt_decision)
        except Exception as e:
            log_action("Analyst Agent", f"GPT failed to interpret: {e}", self.client_id)

        if "analyze" in task["task"].lower():
            self.analyze_performance()
        elif "report" in task["task"].lower():
            self.generate_scaling_report()
        elif "improve" in task["task"].lower():
            self.suggest_improvement()

    def load_pricing(self):
        path = Path("pricing.json")
        if path.exists():
            return json.loads(path.read_text())
        return {}

    def analyze_performance(self):
        leads = self.metrics.get("leads_generated", 0)
        revenue = self.metrics.get("revenue_generated", 0)
        tasks_failed = self.metrics.get("tasks_failed", 0)
        clients = self.metrics.get("clients_onboarded", 0)

        insights = []
        if leads < 50:
            insights.append("Lead volume is low. Recommend enhancing outreach and visibility.")
        if tasks_failed > 5:
            insights.append("High failure rate. Recommend QA on agent logic.")
        if clients < 3:
            insights.append("Client acquisition weak. Recommend CRM + support review.")
        if revenue < 1000:
            insights.append("Low revenue. Recommend monetization and pricing review.")

        for insight in insights:
            log_action("Analyst Agent", f"Insight: {insight}", self.client_id)
            update_task_queue("Manager Agent", {"task": f"Review: {insight}", "priority": 2}, self.client_id)

    def generate_scaling_report(self):
        summary = {
            "leads": self.metrics.get("leads_generated", 0),
            "clients": self.metrics.get("clients_onboarded", 0),
            "revenue": self.metrics.get("revenue_generated", 0),
            "tasks_failed": self.metrics.get("tasks_failed", 0),
            "pricing": self.pricing,
            "recommendation": "Enhance outreach, refine pricing, automate support touchpoints."
        }
        report = json.dumps(summary, indent=2)
        log_action("Analyst Agent", f"Scaling Report:\n{report}", self.client_id)
        update_task_queue("Manager Agent", {"task": "Review latest scaling report", "priority": 2}, self.client_id)

    def suggest_improvement(self):
        update_task_queue("Marketing Agent", {"task": "Optimize campaign targeting", "priority": 2}, self.client_id)
        update_task_queue("CRM Agent", {"task": "Review lead conversion workflow", "priority": 2}, self.client_id)
        log_action("Analyst Agent", "Improvement tasks queued for Marketing and CRM", self.client_id)

    def log_reasoning(self, input_text, output_json):
        log_path = Path(f".digi/clients/{self.client_id}/gpt_reasons.log")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as f:
            f.write(f"[{datetime.now()}] INPUT: {input_text}\nOUTPUT: {output_json}\n\n")
