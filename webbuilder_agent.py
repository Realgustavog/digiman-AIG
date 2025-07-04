# ==================== webbuilder_agent.py (DigiMan OS) ====================

import os
import json
from pathlib import Path
from datetime import datetime
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from core.metrics import increment_metric
from gpt.gpt_router import interpret_command

class WebBuilderAgent:
    def __init__(self, client_id=None):
        # [FEATURE: INIT]
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.webflow_api_key = os.getenv("WEBFLOW_API_KEY")
        self.domain_name = os.getenv("DOMAIN_NAME")
        self.site_path = Path(f".digi/clients/{client_id}/websites.json")
        self.brand_guidelines = self.load_brand_guidelines()
        self.sites = self.load_sites()

    def load_sites(self):
        if self.site_path.exists():
            return json.loads(self.site_path.read_text())
        return []

    def save_sites(self):
        self.site_path.parent.mkdir(parents=True, exist_ok=True)
        self.site_path.write_text(json.dumps(self.sites, indent=2))

    def load_brand_guidelines(self):
        path = Path(f".digi/clients/{self.client_id}/brand.json")
        if path.exists():
            return json.loads(path.read_text())
        return {}

    def run_task(self, task):
        # [FEATURE: RUN_TASK]
        log_action("WebBuilderAgent", f"[RUN_TASK] {task['task']}", self.client_id)
        increment_metric("tasks_processed")

        try:
            gpt_decision = interpret_command(task["task"], self.client_id)
            log_action("WebBuilderAgent", f"[GPT_DECISION] {gpt_decision}", self.client_id)
            task.update(gpt_decision)
        except Exception as e:
            log_action("WebBuilderAgent", f"[ERROR] GPT interpretation failed: {e}", self.client_id)

        # [FEATURE: SITE GENERATION]
        if "website" in task["task"].lower() or "landing page" in task["task"].lower() or "funnel" in task["task"].lower():
            self.generate_site(task)

    def generate_site(self, task):
        # [FEATURE: SITE GENERATION PROMPT]
        prompt = f"""
You are DigiMan WebBuilderAgent.

Generate a detailed landing page or website structure for:
"{task['task']}"

Context:
- Client memory: {" ".join([m["content"] for m in self.memory[-5:] if isinstance(m, dict)])}
- Brand guidelines: {json.dumps(self.brand_guidelines, indent=2)}

Output:
{{
  "site_title": "Landing Page Title",
  "description": "Purpose of the site",
  "sections": ["Hero", "Features", "Testimonials", "CTA"],
  "copy_snippets": ["Header copy", "CTA copy"],
  "color_scheme": ["#000000", "#FFFFFF"],
  "font_preferences": ["Sans Serif"],
  "forms": ["Lead Capture", "Newsletter Signup"],
  "ab_test_variants": ["Variant A description", "Variant B description"],
  "next_task": {{
      "agent": "Marketing Agent",
      "task": "Launch campaign using funnel: Landing Page Title",
      "priority": 2
  }}
}}
"""
        try:
            site_plan = interpret_command(prompt, self.client_id)
            site_entry = {
                "title": site_plan.get("site_title", "Untitled Site"),
                "description": site_plan.get("description", ""),
                "sections": site_plan.get("sections", []),
                "copy_snippets": site_plan.get("copy_snippets", []),
                "color_scheme": site_plan.get("color_scheme", []),
                "fonts": site_plan.get("font_preferences", []),
                "forms": site_plan.get("forms", []),
                "ab_test_variants": site_plan.get("ab_test_variants", []),
                "created_at": datetime.now().isoformat()
            }
            self.sites.append(site_entry)
            self.save_sites()

            # [FEATURE: FOLLOW-UP TASK]
            next_task = site_plan.get("next_task")
            if next_task:
                update_task_queue(next_task["agent"], next_task, self.client_id)
                log_action("WebBuilderAgent", f"[FOLLOW-UP] Queued task: {next_task}", self.client_id)

            log_action("WebBuilderAgent", f"[COMPLETE] Site '{site_entry['title']}' generated and saved.", self.client_id)

        except Exception as e:
            log_action("WebBuilderAgent", f"[ERROR] Failed to generate site plan: {e}", self.client_id)

# ==================== END webbuilder_agent.py ====================

