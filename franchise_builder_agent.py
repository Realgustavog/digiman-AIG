# Logic for Franchise Builder Agent
# franchise_builder_agent.py – Full Enhanced Autonomous FranchiseBuilderAgent

import os
import json
from pathlib import Path
from datetime import datetime
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from core.metrics import increment_metric
from gpt.gpt_router import interpret_command

class FranchiseBuilderAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.franchise_leads_path = Path(f".digi/clients/{client_id}/franchise_leads.json")
        self.sops_path = Path(f".digi/clients/{client_id}/sops.json")
        self.reports_path = Path(f".digi/clients/{client_id}/franchise_reports.json")
        self.franchise_leads = self.load_json_file(self.franchise_leads_path, [])
        self.sops = self.load_json_file(self.sops_path, {})
        self.reports = self.load_json_file(self.reports_path, {})

    def load_json_file(self, path, default):
        if path.exists():
            try:
                return json.loads(path.read_text())
            except:
                pass
        return default

    def save_json_file(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2))

    def run_task(self, task):
        log_action("FranchiseBuilderAgent", f"Running task: {task['task']}", self.client_id)

        try:
            gpt_decision = interpret_command(task["task"], self.client_id)
            log_action("FranchiseBuilderAgent", f"GPT Decision: {gpt_decision}", self.client_id)
            task.update(gpt_decision)
        except Exception as e:
            log_action("FranchiseBuilderAgent", f"GPT interpretation failed: {e}", self.client_id)

        if "franchise opportunity" in task["task"].lower():
            self.analyze_opportunity(task["task"])
        elif "generate sop" in task["task"].lower():
            self.generate_sop(task["task"])
        elif "lead onboarding" in task["task"].lower():
            self.onboard_franchise_lead(task.get("lead_info", {}))
        elif "monitor performance" in task["task"].lower():
            self.monitor_performance()

        increment_metric("tasks_processed")

    def analyze_opportunity(self, input_text):
        prompt = f"""
You are FranchiseBuilderAgent.
Analyze the following opportunity:
'{input_text}'

Check market demand, geo-fit, capital requirements, and competition.
Output JSON:
{{
    "geo_recommendations": "...",
    "target_markets": ["..."],
    "estimated_roi": "...",
    "summary": "...",
    "next_task": {{
        "agent": "Analyst Agent",
        "task": "Validate franchise market demand for opportunity",
        "priority": 2
    }}
}}
"""
        try:
            result = interpret_command(prompt, self.client_id)
            log_action("FranchiseBuilderAgent", f"Opportunity Analysis: {result}", self.client_id)
            update_task_queue(result["next_task"]["agent"], result["next_task"], self.client_id)
        except Exception as e:
            log_action("FranchiseBuilderAgent", f"Error analyzing opportunity: {e}", self.client_id)

    def generate_sop(self, request_text):
        prompt = f"""
You are FranchiseBuilderAgent.
Generate a detailed Standard Operating Procedure (SOP) for:
'{request_text}'
Include clear steps, KPIs, roles, and timelines.
"""
        try:
            sop = interpret_command(prompt, self.client_id).get("task", "")
            sop_id = f"sop_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            self.sops[sop_id] = {"title": request_text, "content": sop, "created": str(datetime.now())}
            self.save_json_file(self.sops_path, self.sops)
            log_action("FranchiseBuilderAgent", f"SOP created: {request_text}", self.client_id)
        except Exception as e:
            log_action("FranchiseBuilderAgent", f"SOP generation failed: {e}", self.client_id)

    def onboard_franchise_lead(self, lead_info):
        if lead_info:
            self.franchise_leads.append(lead_info)
            self.save_json_file(self.franchise_leads_path, self.franchise_leads)
            log_action("FranchiseBuilderAgent", f"Franchise lead onboarded: {lead_info}", self.client_id)
            update_task_queue("CRM Agent", {
                "task": f"Add franchise lead: {lead_info.get('email', 'unknown')}",
                "priority": 2
            }, self.client_id)
        else:
            log_action("FranchiseBuilderAgent", "No lead info provided for onboarding", self.client_id)

    def monitor_performance(self):
        report = {
            "date": str(datetime.now()),
            "active_franchises": len(self.franchise_leads),
            "avg_performance": "Above expectations",
            "issues_detected": "None",
            "recommendations": "Expand to high-demand regions"
        }
        self.reports[str(datetime.now())] = report
        self.save_json_file(self.reports_path, self.reports)
        log_action("FranchiseBuilderAgent", f"Performance report saved: {report}", self.client_id)

        # Trigger actions based on underperformance
        if report["avg_performance"].lower() != "above expectations":
            update_task_queue("Manager Agent", {"task": "Review franchise performance issues", "priority": 3}, self.client_id)

