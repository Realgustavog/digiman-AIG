from pathlib import Path

# Define the save path for enhanced CRM agent
crm_path = Path("/mnt/data/crm_agent.py")

enhanced_crm_code = '''
import json
from pathlib import Path
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from gpt.gpt_router import interpret_command
from datetime import datetime

class CRMAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.leads_path = Path(f".digi/clients/{client_id}/leads.json")
        self.reasons_path = Path(f".digi/clients/{client_id}/gpt_reasons.log")
        self.leads_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.leads_path.exists():
            self.leads_path.write_text(json.dumps([], indent=2))

    def run_task(self, task):
        log_action("CRM Agent", f"Running task: {task['task']}", self.client_id)
        task_text = task["task"].lower()

        try:
            gpt_decision = interpret_command(task["task"], self.client_id)
            task.update(gpt_decision)
            self.log_reasoning(task["task"], gpt_decision)
        except Exception as e:
            log_action("CRM Agent", f"GPT interpretation failed: {e}", self.client_id)

        if "add lead" in task_text:
            self.add_lead(task.get("email"), task.get("source", "unknown"))
        elif "update lead" in task_text:
            self.update_lead_status(task.get("email"), task.get("status"))
        elif "log note" in task_text:
            self.add_note_to_lead(task.get("email"), task.get("note"))

    def load_leads(self):
        return json.loads(self.leads_path.read_text())

    def save_leads(self, leads):
        self.leads_path.write_text(json.dumps(leads, indent=2))

    def add_lead(self, email, source="unknown"):
        leads = self.load_leads()
        if not any(lead["email"] == email for lead in leads):
            new_lead = {
                "email": email,
                "source": source,
                "status": "new",
                "score": 1,
                "notes": [],
                "created_at": datetime.now().isoformat()
            }
            leads.append(new_lead)
            self.save_leads(leads)
            log_action("CRM Agent", f"Added new lead: {email}", self.client_id)
            update_task_queue("Sales Agent", {"task": f"Pitch lead: {email}", "priority": 2}, self.client_id)
        else:
            log_action("CRM Agent", f"Lead already exists: {email}", self.client_id)

    def update_lead_status(self, email, status):
        leads = self.load_leads()
        for lead in leads:
            if lead["email"] == email:
                lead["status"] = status
                self.save_leads(leads)
                log_action("CRM Agent", f"Updated lead status: {email} → {status}", self.client_id)
                return
        log_action("CRM Agent", f"Lead not found: {email}", self.client_id)

    def add_note_to_lead(self, email, note):
        leads = self.load_leads()
        for lead in leads:
            if lead["email"] == email:
                lead["notes"].append(note)
                self.save_leads(leads)
                log_action("CRM Agent", f"Added note to lead: {email}", self.client_id)
                return
        log_action("CRM Agent", f"Lead not found for note: {email}", self.client_id)

    def log_reasoning(self, input_text, output_json):
        self.reasons_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.reasons_path, "a") as f:
            f.write(f"[{datetime.now()}] INPUT: {input_text}\\nOUTPUT: {output_json}\\n\\n")
