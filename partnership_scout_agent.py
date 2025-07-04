# partnership_scout_agent.py - DigiMan Partnership Scout Agent

import json
from pathlib import Path
from datetime import datetime
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from core.metrics import increment_metric
from gpt.gpt_router import interpret_command

class PartnershipScoutAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.partners_log = Path(f".digi/clients/{client_id}/partners_identified.json")
        self.partners_log.parent.mkdir(parents=True, exist_ok=True)
        if not self.partners_log.exists():
            self.partners_log.write_text(json.dumps([], indent=2))

    def run_task(self, task):
        log_action("Partnership Scout Agent", f"Running task: {task['task']}", self.client_id)
        increment_metric("tasks_processed")
        self.identify_partnership_opportunities(task)

    def identify_partnership_opportunities(self, task):
        prompt = f"""
You are DigiMan's Partnership Scout Agent. Using past memory:
{json.dumps([m['content'] for m in self.memory[-5:] if 'content' in m], indent=2)}

Task: {task['task']}

Identify 3 potential strategic partners, rate priority 1-3, and suggest outreach draft. Respond in JSON:
{{
    "partners": [
        {{"name": "...", "industry": "...", "reason": "...", "priority": 1-3}}
    ],
    "outreach_script": "..."
}}
"""
        try:
            result = interpret_command(prompt, self.client_id)
            self.log_gpt_reasoning(prompt, result)

            partners = result.get("partners", [])
            outreach_script = result.get("outreach_script", "")

            current_partners = json.loads(self.partners_log.read_text())
            current_partners.extend(partners)
            self.partners_log.write_text(json.dumps(current_partners, indent=2))

            for partner in partners:
                agent_task = {
                    "task": f"Initiate outreach to potential partner: {partner['name']} - {partner['reason']}",
                    "priority": partner.get("priority", 2)
                }
                update_task_queue("Outreach Agent", agent_task, self.client_id)

                if partner.get("priority", 2) == 3:
                    update_task_queue("Sales Agent", {
                        "task": f"Engage high-priority partner lead: {partner['name']}",
                        "priority": 3
                    }, self.client_id)

            log_action("Partnership Scout Agent",
                       f"Identified {len(partners)} partners, outreach prepared, script ready.",
                       self.client_id)

        except Exception as e:
            log_action("Partnership Scout Agent", f"GPT error: {e}", self.client_id)

    def log_gpt_reasoning(self, prompt, response):
        log_file = Path(f".digi/clients/{self.client_id}/gpt_reasons.log")
        with open(log_file, "a") as f:
            f.write(f"[{datetime.now()}] PARTNERSHIP SCOUT PROMPT:\n{prompt}\nRESPONSE:\n{json.dumps(response, indent=2)}\n\n")

