# ==================== visuals_agent.py (DigiMan OS) ====================

import os
import json
from pathlib import Path
from datetime import datetime
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from core.metrics import increment_metric
from gpt.gpt_router import interpret_command

class VisualsAgent:
    def __init__(self, client_id=None):
        # [FEATURE: INIT]
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.visuals_path = Path(f".digi/clients/{client_id}/visuals_briefs.json")
        self.visuals = self.load_visuals()
        self.brand_guidelines = self.load_brand_guidelines()

    def load_visuals(self):
        if self.visuals_path.exists():
            return json.loads(self.visuals_path.read_text())
        return []

    def save_visuals(self):
        self.visuals_path.parent.mkdir(parents=True, exist_ok=True)
        self.visuals_path.write_text(json.dumps(self.visuals, indent=2))

    def load_brand_guidelines(self):
        path = Path(f".digi/clients/{self.client_id}/brand.json")
        if path.exists():
            return json.loads(path.read_text())
        return {}

    def run_task(self, task):
        # [FEATURE: RUN_TASK]
        log_action("VisualsAgent", f"[RUN_TASK] {task['task']}", self.client_id)
        increment_metric("tasks_processed")

        try:
            gpt_decision = interpret_command(task["task"], self.client_id)
            log_action("VisualsAgent", f"[GPT_DECISION] {gpt_decision}", self.client_id)
            task.update(gpt_decision)
        except Exception as e:
            log_action("VisualsAgent", f"[ERROR] GPT interpretation failed: {e}", self.client_id)

        # [FEATURE: VISUAL BRIEF GENERATION]
        if "visual" in task["task"].lower() or "design" in task["task"].lower():
            self.generate_visual_brief(task)

    def generate_visual_brief(self, task):
        # [FEATURE: BRIEF GENERATION]
        prompt = f"""
You are DigiMan VisualsAgent.

Generate a clear, creative, brand-aligned visual brief for:
"{task['task']}"

Context:
- Client memory: {" ".join([m["content"] for m in self.memory[-5:] if isinstance(m, dict)])}
- Brand guidelines: {json.dumps(self.brand_guidelines, indent=2)}
- Provide:
{{
  "title": "Post Title",
  "description": "Detailed design description",
  "suggested_colors": ["#000000", "#FFFFFF"],
  "font_preferences": ["Sans Serif"],
  "platforms": ["Instagram", "LinkedIn"],
  "captions": ["Caption with call-to-action"],
  "hashtags": ["#AI", "#Automation"],
  "split_test_variants": ["Variant A desc", "Variant B desc"],
  "next_task": {{
      "agent": "Socials Agent",
      "task": "Schedule post using visual asset: {task['task']}",
      "priority": 2
  }}
}}
"""
        try:
            brief = interpret_command(prompt, self.client_id)
            title = brief.get("title", "Untitled Visual")
            self.visuals.append({
                "title": title,
                "description": brief.get("description", ""),
                "colors": brief.get("suggested_colors", []),
                "fonts": brief.get("font_preferences", []),
                "platforms": brief.get("platforms", []),
                "captions": brief.get("captions", []),
                "hashtags": brief.get("hashtags", []),
                "split_test_variants": brief.get("split_test_variants", []),
                "created_at": datetime.now().isoformat()
            })
            self.save_visuals()

            # [FEATURE: FOLLOW-UP TASK QUEUE]
            next_task = brief.get("next_task")
            if next_task:
                update_task_queue(next_task["agent"], next_task, self.client_id)
                log_action("VisualsAgent", f"[FOLLOW-UP] Queued task: {next_task}", self.client_id)

            log_action("VisualsAgent", f"[COMPLETE] Visual brief '{title}' saved.", self.client_id)

        except Exception as e:
            log_action("VisualsAgent", f"[ERROR] Failed to generate visual brief: {e}", self.client_id)

# ==================== END visuals_agent.py ====================
