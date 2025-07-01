# Logic for Analyst Agent
import json
from core.metrics import metrics
from core.memory_store import load_memory
from core.digiman_core import log_action

class AnalystAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.metrics = metrics

    def run_task(self, task):
        log_action("Analyst Agent", f"Running task: {task['task']}", self.client_id)
        if "analyze" in task["task"].lower():
            self.analyze_performance()
        elif "report" in task["task"].lower():
            self.generate_scaling_report()

    def analyze_performance(self):
        leads = self.metrics.get("leads_generated", 0)
        revenue = self.metrics.get("revenue_generated", 0)
        tasks_failed = self.metrics.get("tasks_failed", 0)
        clients = self.metrics.get("clients_onboarded", 0)

        insights = []
        if leads < 50:
            insights.append("Lead volume is low. Suggest increasing outreach or content campaigns.")
        if tasks_failed > 5:
            insights.append("High task failure rate. Suggest reviewing failing agent logic.")
        if clients < 3:
            insights.append("Client acquisition is below goal. Review onboarding and CRM effectiveness.")
        if revenue < 1000:
            insights.append("Revenue is below threshold. Recommend monetization review.")

        for insight in insights:
            log_action("Analyst Agent", f"Insight: {insight}", self.client_id)

    def generate_scaling_report(self):
        summary = {
            "leads": self.metrics.get("leads_generated", 0),
            "clients": self.metrics.get("clients_onboarded", 0),
            "revenue": self.metrics.get("revenue_generated", 0),
            "tasks_failed": self.metrics.get("tasks_failed", 0),
            "recommendation": "Expand paid channels, optimize onboarding, and review underperforming agents."
        }
        report = json.dumps(summary, indent=2)
        log_action("Analyst Agent", f"Scaling report generated:\n{report}", sel
