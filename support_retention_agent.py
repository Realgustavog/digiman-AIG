# ==================== support_retention_agent.py (DigiMan OS) ====================

import json
from pathlib import Path
from datetime import datetime
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from core.metrics import increment_metric
from gpt.gpt_router import interpret_command

class SupportRetentionAgent:
    def __init__(self, client_id=None):
        # [INIT]
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.tickets_path = Path(f".digi/clients/{client_id}/support_tickets.json")
        self.tickets = self.load_tickets()

    def load_tickets(self):
        if self.tickets_path.exists():
            return json.loads(self.tickets_path.read_text())
        return []

    def save_tickets(self):
        self.tickets_path.parent.mkdir(parents=True, exist_ok=True)
        self.tickets_path.write_text(json.dumps(self.tickets, indent=2))

    def run_task(self, task):
        log_action("SupportRetentionAgent", f"[RUN_TASK] {task['task']}", self.client_id)
        increment_metric("tasks_processed")

        try:
            gpt_decision = interpret_command(task["task"], self.client_id)
            log_action("SupportRetentionAgent", f"[GPT_DECISION] {gpt_decision}", self.client_id)
            task.update(gpt_decision)
        except Exception as e:
            log_action("SupportRetentionAgent", f"[ERROR] GPT interpretation failed: {e}", self.client_id)

        # [TASK ROUTING BASED ON CONTENT]
        if "support" in task["task"].lower() or "ticket" in task["task"].lower():
            self.handle_ticket(task)
        elif "churn" in task["task"].lower() or "retain" in task["task"].lower():
            self.prevent_churn()

    def handle_ticket(self, task):
        # [FEATURE: TICKET HANDLING]
        ticket = {
            "task": task["task"],
            "timestamp": datetime.now().isoformat(),
            "status": "open",
            "priority": task.get("priority", 2)
        }
        self.tickets.append(ticket)
        self.save_tickets()
        log_action("SupportRetentionAgent", f"Ticket logged: {task['task']}", self.client_id)

        # [FEATURE: AUTO-ESCALATION]
        if "urgent" in task["task"].lower() or ticket["priority"] >= 3:
            update_task_queue("Manager Agent", {
                "task": f"Urgent support ticket: {task['task']}",
                "priority": 3
            }, self.client_id)
            log_action("SupportRetentionAgent", "Escalated urgent support ticket to ManagerAgent.", self.client_id)

        # [FEATURE: AUTO-RESOLUTION ATTEMPT VIA GPT]
        prompt = f"""
You are DigiMan SupportRetentionAgent.

Resolve or propose actions for:
{task['task']}

Context:
{json.dumps(self.tickets[-3:], indent=2)}

Respond with a JSON:
{{
  "resolution_attempt": "Response message to send to client",
  "follow_up_task": {{
    "agent": "CRM Agent",
    "task": "Follow up with client regarding resolution",
    "priority": 2
  }}
}}
"""
        try:
            resolution = interpret_command(prompt, self.client_id)
            message = resolution.get("resolution_attempt", "Thank you for contacting support. We are addressing your issue.")
            follow_up = resolution.get("follow_up_task")

            if follow_up:
                update_task_queue(follow_up["agent"], follow_up, self.client_id)
                log_action("SupportRetentionAgent", f"Follow-up task queued: {follow_up}", self.client_id)

            log_action("SupportRetentionAgent", f"Resolution attempt: {message}", self.client_id)

        except Exception as e:
            log_action("SupportRetentionAgent", f"[ERROR] Resolution attempt failed: {e}", self.client_id)

    def prevent_churn(self):
        # [FEATURE: PROACTIVE RETENTION]
        prompt = f"""
You are DigiMan SupportRetentionAgent.

Analyze client memory and current tickets to detect churn risk or dissatisfaction.

Memory:
{" ".join([m["content"] for m in self.memory[-5:] if isinstance(m, dict)])}

Tickets:
{json.dumps(self.tickets[-3:], indent=2)}

Respond with JSON:
{{
  "churn_risk": true | false,
  "reason": "Detected churn signals such as cancellation mention",
  "retention_action": {{
    "agent": "Sales Agent",
    "task": "Offer loyalty discount to prevent churn",
    "priority": 3
  }}
}}
"""
        try:
            churn_check = interpret_command(prompt, self.client_id)
            churn_risk = churn_check.get("churn_risk", False)
            reason = churn_check.get("reason", "No specific reason provided.")

            if churn_risk:
                retention_task = churn_check.get("retention_action")
                if retention_task:
                    update_task_queue(retention_task["agent"], retention_task, self.client_id)
                    log_action("SupportRetentionAgent", f"Churn risk detected: {reason}. Retention action triggered.", self.client_id)
            else:
                log_action("SupportRetentionAgent", "No churn risk detected at this time.", self.client_id)

        except Exception as e:
            log_action("SupportRetentionAgent", f"[ERROR] Churn prevention failed: {e}", self.client_id)

# ==================== END support_retention_agent.py ====================
