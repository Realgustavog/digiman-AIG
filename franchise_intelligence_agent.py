# Logic for FranchiseIntelligenceAgent
import os
import json
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from core.metrics import increment_metric
from gpt.gpt_router import interpret_command
from datetime import datetime
from pathlib import Path

class FranchiseIntelligenceAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.reports_path = Path(f".digi/clients/{client_id}/franchise_reports.json")
        self.reports_path.parent.mkdir(parents=True, exist_ok=True)

    def run_task(self, task):
        log_action("FranchiseIntelligenceAgent", f"Running task: {task['task']}", self.client_id)
        increment_metric("tasks_processed")

        try:
            if "monitor" in task["task"].lower() or "analysis" in task["task"].lower():
                self.analyze_market(task)
            elif "forecast" in task["task"].lower():
                self.generate_forecast(task)
            else:
                self.analyze_market(task)
        except Exception as e:
            log_action("FranchiseIntelligenceAgent", f"Error: {e}", self.client_id)

    def analyze_market(self, task):
        prompt = f"""
You are DigiMan's FranchiseIntelligenceAgent.

Your mission:
- Analyze live market data for franchise expansion.
- Identify competitor density, market demand, pricing trends.
- Suggest ideal regions or cities for expansion.
- Collaborate with FranchiseBuilderAgent and AnalystAgent.

Context memory:
{json.dumps(self.memory[-5:], indent=2)}

Task:
{task['task']}

Respond in JSON:
{{
    "recommendation": "Expand in Austin, TX targeting tech service franchises.",
    "competitor_summary": "3 main competitors with average prices 10% higher than our proposed model.",
    "demand_trend": "Upward demand in the last 6 months by 22%.",
    "next_task": {{
        "agent": "FranchiseBuilderAgent",
        "task": "Prepare expansion package for Austin, TX.",
        "priority": 2
    }}
}}
"""
        try:
            result = interpret_command(prompt, self.client_id)
            log_action("FranchiseIntelligenceAgent", f"GPT Analysis: {result}", self.client_id)
            self.save_report(result)

            if "next_task" in result:
                update_task_queue(result["next_task"]["agent"], result["next_task"], self.client_id)

        except Exception as e:
            log_action("FranchiseIntelligenceAgent", f"GPT error: {e}", self.client_id)

    def generate_forecast(self, task):
        prompt = f"""
You are DigiMan's FranchiseIntelligenceAgent.

Generate a 6-month franchise growth forecast using memory data, market trends, and competitor analysis.

Provide:
- Expected new customers per location.
- Projected MRR increase.
- Recommended marketing budget.
- Cities with highest ROI potential.

Respond in JSON:
{{
    "forecast": {{
        "expected_customers_per_location": 120,
        "projected_MRR_increase": "$4500 per location",
        "recommended_marketing_budget": "$2000 per location",
        "best_cities": ["Austin, TX", "Charlotte, NC", "Denver, CO"]
    }},
    "next_task": {{
        "agent": "MarketingAgent",
        "task": "Plan launch campaigns for recommended cities with $2000 budget each.",
        "priority": 3
    }}
}}
"""
        try:
            result = interpret_command(prompt, self.client_id)
            log_action("FranchiseIntelligenceAgent", f"Forecast generated: {result}", self.client_id)
            self.save_report(result)

            if "next_task" in result:
                update_task_queue(result["next_task"]["agent"], result["next_task"], self.client_id)

        except Exception as e:
            log_action("FranchiseIntelligenceAgent", f"Forecast error: {e}", self.client_id)

    def save_report(self, report):
        reports = []
        if self.reports_path.exists():
            reports = json.loads(self.reports_path.read_text())
        reports.append({
            "timestamp": datetime.now().isoformat(),
            "report": report
        })
        self.reports_path.write_text(json.dumps(reports, indent=2))
        log_action("FranchiseIntelligenceAgent", f"Report saved.", self.client_id)
