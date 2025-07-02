from pathlib import Path

# Define path for enhanced manager_agent.py
manager_agent_path = Path("/mnt/data/manager_agent.py")

enhanced_manager_code = '''
# Logic for Manager Agent
import json
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from core.metrics import metrics
from gpt.gpt_router import interpret_command
from datetime import datetime
from pathlib import Path

class ManagerAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.metrics = metrics
        self.business_phases = ["setup", "promotion", "sales", "onboarding", "client_ops"]
        self.phase_path = Path(f".digi/clients/{client_id}/phase.json")
        self.reasoning_log = Path(f".digi/clients/{client_id}/gpt_reasons.log")
        self.current_phase_index = self.load_current_phase_index()

    def run_task(self, task):
        log_action("Manager Agent", f"Running task: {task['task']}", self.client_id)

        try:
            gpt_decision = interpret_command(task["task"], self.client_id)
            log_action("Manager Agent", f"GPT Decision: {gpt_decision}", self.client_id)
            self.log_reasoning(task["task"], gpt_decision)
            task.update(gpt_decision)
        except Exception as e:
            log_action("Manager Agent", f"GPT decision error: {e}", self.client_id)

        self.monitor_performance()
        self.evaluate_phase_transition()
        self.delegate_based_on_priority()

    def load_current_phase_index(self):
        try:
            if self.phase_path.exists():
                data = json.loads(self.phase_path.read_text())
                return self.business_phases.index(data["phase"])
        except:
            pass
        return 0

    def save_current_phase_index(self):
        self.phase_path.parent.mkdir(parents=True, exist_ok=True)
        self.phase_path.write_text(json.dumps({"phase": self.business_phases[self.current_phase_index]}, indent=2))

    def monitor_performance(self):
        if self.metrics["tasks_failed"] > 5:
            update_task_queue("Support Agent", {"task": "Investigate failures", "priority": 3}, self.client_id)
        if self.metrics["leads_generated"] < 10:
            update_task_queue("Outreach Agent", {"task": "Increase outreach", "priority": 3}, self.client_id)
        log_action("Manager Agent", f"Performance Review: {json.dumps(self.metrics)}", self.client_id)

    def evaluate_phase_transition(self):
        if self.metrics["clients_onboarded"] >= 5 and self.current_phase_index < len(self.business_phases) - 1:
            self.current_phase_index += 1
            self.save_current_phase_index()
            log_action("Manager Agent", f"Phase transitioned to: {self.business_phases[self.current_phase_index]}", self.client_id)

    def delegate_based_on_priority(self):
        phase = self.business_phases[self.current_phase_index]
        if phase == "setup":
            update_task_queue("Scout Agent", {"task": "Identify market niches", "priority": 2}, self.client_id)
        elif phase == "promotion":
            update_task_queue("Marketing Agent", {"task": "Run lead gen campaign", "priority": 2}, self.client_id)
        elif phase == "sales":
            update_task_queue("Sales Agent", {"task": "Close active leads", "priority": 3}, self.client_id)
        elif phase == "onboarding":
            update_task_queue("Client Onboarding Agent", {"task": "Onboard new clients", "priority": 2}, self.client_id)
        elif phase == "client_ops":
            update_task_queue("Retention Agent", {"task": "Optimize existing client performance", "priority": 2}, self.client_id)

    def log_reasoning(self, input_text, output_json):
        self.reasoning_log.parent.mkdir(parents=True, exist_ok=True)
        with open(self.reasoning_log, "a") as f:
            f.write(f"[{datetime.now()}] INPUT: {input_text}\\nOUTPUT: {output_json}\\n\\n")
'''

# Save the enhanced manager_agent.py
manager_agent_path.write_text(enhanced_manager_code.strip())

str(manager_agent_path)


