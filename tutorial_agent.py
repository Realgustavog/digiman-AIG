# ==================== tutorial_agent.py (DigiMan OS) ====================

import os
import json
from datetime import datetime
from pathlib import Path
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from core.metrics import increment_metric
from gpt.gpt_router import interpret_command

class TutorialAgent:
    def __init__(self, client_id=None):
        # [INIT]
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.tutorials_path = Path(f".digi/clients/{client_id}/tutorials.json")
        self.tutorials = self.load_tutorials()

    def load_tutorials(self):
        if self.tutorials_path.exists():
            return json.loads(self.tutorials_path.read_text())
        return []

    def save_tutorials(self):
        self.tutorials_path.parent.mkdir(parents=True, exist_ok=True)
        self.tutorials_path.write_text(json.dumps(self.tutorials, indent=2))

    def run_task(self, task):
        log_action("TutorialAgent", f"[RUN_TASK] {task['task']}", self.client_id)
        increment_metric("tasks_processed")

        try:
            gpt_decision = interpret_command(task["task"], self.client_id)
            log_action("TutorialAgent", f"[GPT_DECISION] {gpt_decision}", self.client_id)
            task.update(gpt_decision)
        except Exception as e:
            log_action("TutorialAgent", f"[ERROR] GPT interpretation failed: {e}", self.client_id)

        # [FEATURE: TUTORIAL GENERATION]
        if "tutorial" in task["task"].lower() or "guide" in task["task"].lower():
            self.generate_tutorial(task)

    def generate_tutorial(self, task):
        prompt = f"""
You are DigiMan TutorialAgent.

Generate a clear, actionable tutorial for the client's requested topic:
"{task['task']}"

Context:
- Client memory: {" ".join([m["content"] for m in self.memory[-5:] if isinstance(m, dict)])}
- Ensure steps are simple, structured, and clear.
- Add tips for best practice.
- Format as JSON:
{{
  "title": "Title of Tutorial",
  "steps": ["Step 1", "Step 2", "..."],
  "tips": ["Tip 1", "Tip 2"],
  "suggested_next_task": {{
      "agent": "Support Agent",
      "task": "Check in on client after tutorial",
      "priority": 2
  }}
}}
"""
        try:
            tutorial = interpret_command(prompt, self.client_id)
            title = tutorial.get("title", "Untitled Tutorial")
            self.tutorials.append({
                "title": title,
                "steps": tutorial.get("steps", []),
                "tips": tutorial.get("tips", []),
                "created_at": datetime.now().isoformat()
            })
            self.save_tutorials()

            # [FEATURE: FOLLOW-UP]
            suggested_task = tutorial.get("suggested_next_task")
            if suggested_task:
                update_task_queue(suggested_task["agent"], suggested_task, self.client_id)
                log_action("TutorialAgent", f"Suggested follow-up task queued: {suggested_task}", self.client_id)

            log_action("TutorialAgent", f"Tutorial '{title}' generated and saved.", self.client_id)

        except Exception as e:
            log_action("TutorialAgent", f"[ERROR] Tutorial generation failed: {e}", self.client_id)

# ==================== END tutorial_agent.py ====================
