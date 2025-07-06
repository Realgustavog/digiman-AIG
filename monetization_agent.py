import json
import os
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from core.metrics import (
    metrics, add_revenue_for_client, update_forecast, increment_metric
)
from gpt.gpt_router import interpret_command
from pathlib import Path
from datetime import datetime

class MonetizationAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.pricing_file = Path("pricing.json")
        self.current_pricing = self.load_pricing()
        self.client_leads_path = Path(f".digi/clients/{client_id}/leads.json")
        self.client_revenue_path = Path(f".digi/clients/{client_id}/revenue.json")

    def run_task(self, task):
        log_action("Monetization Agent", f"Running task: {task['task']}", self.client_id)

        try:
            gpt_decision = interpret_command(
                f"As Monetization Strategist, handle: {task['task']}", self.client_id)
            log_action("Monetization Agent", f"GPT Task Decision: {gpt_decision}", self.client_id)
            task.update(gpt_decision)
        except Exception as e:
            log_action("Monetization Agent", f"GPT failed to parse: {e}", self.client_id)

        if "pricing" in task["task"].lower():
            self.analyze_pricing()
        elif "forecast" in task["task"].lower():
            self.generate_forecast()
        elif "segment" in task["task"].lower():
            self.segment_clients()

    def load_pricing(self):
        if self.pricing_file.exists():
            return json.loads(self.pricing_file.read_text())
        return {}

    def load_client_leads(self):
        if self.client_leads_path.exists():
            return json.loads(self.client_leads_path.read_text())
        return []

    def analyze_pricing(self):
        prompt = f"""
You are a Monetization Strategist. Based on current pricing:
{json.dumps(self.current_pricing)}

Propose:
- Better plan names
- Upsell packages
- Monthly vs annual strategies
- Features that should be added or removed per tier
"""
        suggestion = interpret_command(prompt, self.client_id)
        log_action("Monetization Agent", f"Pricing Enhancement Proposal: {suggestion}", self.client_id)
        update_task_queue("Manager Agent", {
            "task": f"Evaluate new pricing strategy: {suggestion}",
            "priority": 2
        }, self.client_id)

    def generate_forecast(self):
        leads = self.load_client_leads()
        total_rev = metrics.get("revenue_generated", 0)
        total_clients = metrics.get("clients_onboarded", 1)
        avg = total_rev / total_clients if total_clients > 0 else 0

        forecast = {
            "monthly_revenue_forecast": round(avg * total_clients * 1.1, 2),
            "projected_growth_rate": "10-15%",
            "leads_considered": len(leads),
            "notes": "Data enriched via GPT and live memory context"
        }
        update_forecast(forecast)
        log_action("Monetization Agent", f"Updated forecast: {forecast}", self.client_id)

    def segment_clients(self):
        # In a real case, would scan multiple client revenue files
        if self.client_revenue_path.exists():
            revenue_data = json.loads(self.client_revenue_path.read_text())
            high = {k: v for k, v in revenue_data.items() if v >= 500}
            low = {k: v for k, v in revenue_data.items() if v < 500}
            update_task_queue("Subscription Agent", {
                "task": f"Review high-value clients for upsell: {json.dumps(high)}",
                "priority": 2
            }, self.client_id)
            update_task_queue("Support Agent", {
                "task": f"Retention risk on low revenue clients: {json.dumps(low)}",
                "priority": 1
            }, self.client_id)
