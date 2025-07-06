import json
from pathlib import Path
from datetime import datetime, timedelta
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from core.metrics import increment_metric
from gpt.gpt_router import interpret_command

class ScoutAgent:
    def __init__(self, client_id=None):
        # === INIT (CLIENT CONTEXT) ===
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.last_run_path = Path(f".digi/clients/{client_id}/scout_last_run.json")
        self.load_last_run()

    def load_last_run(self):
        if self.last_run_path.exists():
            try:
                data = json.loads(self.last_run_path.read_text())
                self.last_run = datetime.fromisoformat(data["last_run"])
            except:
                self.last_run = datetime.min
        else:
            self.last_run = datetime.min

    def save_last_run(self):
        self.last_run_path.parent.mkdir(parents=True, exist_ok=True)
        self.last_run_path.write_text(json.dumps({"last_run": datetime.now().isoformat()}, indent=2))

    def run_task(self, task):
        log_action("Scout Agent", f"[RUN_TASK] Running task: {task['task']}", self.client_id)
        increment_metric("tasks_processed")
        try:
            gpt_result = interpret_command(task["task"], self.client_id)
            log_action("Scout Agent", f"[GPT_DECISION] {gpt_result}", self.client_id)
            task.update(gpt_result)
        except Exception as e:
            log_action("Scout Agent", f"[ERROR] GPT interpretation failed: {e}", self.client_id)

        if "scout" in task["task"].lower() or "research" in task["task"].lower():
            self.scout_market()
        else:
            log_action("Scout Agent", "[SKIP] Task did not match scout pattern.", self.client_id)

    def scout_market(self):
        # === [FEATURE: MARKET & LEAD SCOUTING] ===
        context = "\n".join([m["content"] for m in self.memory[-5:] if isinstance(m, dict) and m.get("role") == "user"])
        prompt = f"""
You are the Scout Agent for DigiMan. Your job is to:
- Research emerging markets and lead sources.
- Find forums, communities, and channels for targeted leads.
- Identify new niches relevant to the client's ICP.

Context:
{context}

Respond in JSON:
{{
  "niches": ["example niche 1", "example niche 2"],
  "platforms": ["Reddit", "LinkedIn", "Facebook Groups"],
  "recommendation": "Focus on AI agency owners on LinkedIn groups for high-ticket leads.",
  "next_task": {{
    "agent": "Outreach Agent",
    "task": "Engage prospects in recommended LinkedIn groups.",
    "priority": 2
  }}
}}
"""
        try:
            scout_data = interpret_command(prompt, self.client_id)
            log_action("Scout Agent", f"[SCOUT_RESULT] {scout_data}", self.client_id)

            recommendation = scout_data.get("recommendation", "Continue current outreach.")
            next_task = scout_data.get("next_task")
            niches = scout_data.get("niches", [])
            platforms = scout_data.get("platforms", [])

            log_action("Scout Agent", f"[RECOMMENDATION] {recommendation}", self.client_id)
            log_action("Scout Agent", f"[NICHES] {niches}", self.client_id)
            log_action("Scout Agent", f"[PLATFORMS] {platforms}", self.client_id)

            if next_task:
                update_task_queue(next_task["agent"], next_task, self.client_id)

            increment_metric("leads_generated")
            self.save_last_run()

        except Exception as e:
            log_action("Scout Agent", f"[ERROR] During scout_market: {e}", self.client_id)

    def auto_trigger(self):
        # === [FEATURE: PERIODIC AUTO-TRIGGER] ===
        now = datetime.now()
        if (now - self.last_run) >= timedelta(days=7):
            log_action("Scout Agent", "[AUTO_TRIGGER] Weekly scout auto-trigger activated.", self.client_id)
            self.scout_market()
        else:
            log_action("Scout Agent", "[AUTO_TRIGGER] Not due yet.", self.client_id)

