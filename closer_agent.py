# Logic for Closer Agent
from pathlib import Path

# Define path for enhanced closer_agent.py
closer_agent_path = Path("/mnt/data/closer_agent.py")

enhanced_closer_agent_code = '''
import os
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from core.metrics import metrics
from gpt.gpt_router import interpret_command
from datetime import datetime
from pathlib import Path

class CloserAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.required_keys = ["TWILIO_SID", "TWILIO_TOKEN"]
        self.active = all(os.getenv(k) for k in self.required_keys)

    def run_task(self, task):
        log_action("Closer Agent", f"Running task: {task['task']}", self.client_id)

        try:
            decision = interpret_command(task["task"], self.client_id)
            log_action("Closer Agent", f"GPT decision: {decision}", self.client_id)
            self.log_reasoning(task["task"], decision)
            task.update(decision)
        except Exception as e:
            log_action("Closer Agent", f"GPT interpretation failed: {e}", self.client_id)

        if "close deal" in task["task"].lower():
            self.handle_closure()

    def handle_closure(self):
        if not self.active:
            log_action("Closer Agent", "Mock deal closed (Twilio inactive)", self.client_id)
            metrics["revenue_generated"] += 1000
            update_task_queue("CRM Agent", {"task": "Update deal status", "priority": 2}, self.client_id)
            return

        reasoning = "Client expressed readiness and pain point resolution. Escalating to CRM."
        metrics["revenue_generated"] += 1500
        update_task_queue("CRM Agent", {"task": "Client marked as closed-won", "priority": 2}, self.client_id)
        update_task_queue("Support Agent", {"task": "Welcome and onboarding follow-up", "priority": 2}, self.client_id)
        log_action("Closer Agent", f"Closed deal: {reasoning}", self.client_id)

    def log_reasoning(self, input_text, output_json):
        log_path = Path(f".digi/clients/{self.client_id}/gpt_reasons.log")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as f:
            f.write(f"[{datetime.now()}] INPUT: {input_text}\\nOUTPUT: {output_json}\\n\\n")
'''

# Save the enhanced closer_agent.py
closer_agent_path.write_text(enhanced_closer_agent_code.strip())

str(closer_agent_path)
