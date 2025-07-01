import json
from core.metrics import metrics
from core.memory_store import load_memory
from core.digiman_core import log_action
from pathlib import Path

class AnalystAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.metrics = metrics
        self.pricing = self.load_pricing()

    def run_task(self, task):
        log_action("Analyst Agent", f"Running task: {task['task']}", self.client_id)
        if "analyze" in task["task"].lower():
            self.analyze_performance()
        elif "report" in task["task"].lower():
            self.generate_scaling_report()

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
            insights.append("Lead volume is low. Suggest increasing outreach or content campaigns.")
        if tasks_failed > 5:
            insights.append("High task failure rate. Suggest reviewing agent logic or APIs.")
        if clients < 3:
            insights.append("Client acquisition is low. CRM or onboarding funnel may need review.")
        if revenue < 1000:
            insights.append("Revenue underperforming. Evaluate monetization and pricing alignment.")

        for insight in insights:
            log_action("Analyst Agent", f"Insight: {insight}", self.client_id)

    def generate_scaling_report(self):
        summary = {
            "leads": self.metrics.get("leads_generated", 0),
            "clients": self.metrics.get("clients_onboarded", 0),
            "revenue": self.metrics.get("revenue_generated", 0),
            "tasks_failed": self.metrics.get("tasks_failed", 0),
            "pricing": self.pricing,
            "recommendation": "Optimize outreach, refine pricing structure, evaluate LTV per tier."
        }
        report = json.dumps(summary, indent=2)
        log_action("Analyst Agent", f"Scaling report:\n{report}", self.client_id)
