# ==================== SocialsAgent.py (DigiMan OS) ====================

import json
from pathlib import Path
from datetime import datetime, timedelta
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from core.metrics import increment_metric
from gpt.gpt_router import interpret_command

class SocialsAgent:
    def __init__(self, client_id=None):
        # === INIT (CLIENT CONTEXT) ===
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.last_post_log = Path(f".digi/clients/{client_id}/socials_last_post.json")
        self.load_last_post_date()

    def load_last_post_date(self):
        if self.last_post_log.exists():
            try:
                data = json.loads(self.last_post_log.read_text())
                self.last_post_date = datetime.fromisoformat(data["last_post"])
            except:
                self.last_post_date = datetime.min
        else:
            self.last_post_date = datetime.min

    def save_last_post_date(self):
        self.last_post_log.parent.mkdir(parents=True, exist_ok=True)
        self.last_post_log.write_text(json.dumps({"last_post": datetime.now().isoformat()}, indent=2))

    def run_task(self, task):
        log_action("Socials Agent", f"[RUN_TASK] {task['task']}", self.client_id)
        increment_metric("tasks_processed")
        try:
            gpt_result = interpret_command(task["task"], self.client_id)
            log_action("Socials Agent", f"[GPT_DECISION] {gpt_result}", self.client_id)
            task.update(gpt_result)
        except Exception as e:
            log_action("Socials Agent", f"[ERROR] GPT interpretation failed: {e}", self.client_id)

        if "post" in task["task"].lower() or "schedule" in task["task"].lower():
            self.create_and_post_content()
        elif "auto" in task["task"].lower():
            self.auto_post_trigger()

    def create_and_post_content(self):
        # === [FEATURE: GPT CONTENT CREATION + SCHEDULING] ===
        context = "\n".join([m["content"] for m in self.memory[-5:] if isinstance(m, dict) and m.get("role") == "user"])
        prompt = f"""
You are the Socials Agent for DigiMan, responsible for:
- Creating high-engagement posts for IG, LinkedIn, Twitter.
- Writing catchy captions and strong CTAs.
- Proposing two A/B variants for testing.
- Considering ICP, tone, and context.

User memory:
{context}

Respond in JSON:
{{
  "platforms": ["Instagram", "LinkedIn"],
  "post_1": {{
    "caption": "Unlock growth with AI agents.",
    "cta": "DM us 'AI' to get started!"
  }},
  "post_2": {{
    "caption": "Struggling to scale? Let AI run your operations.",
    "cta": "Comment 'Scale' below if you're ready."
  }},
  "recommended_time": "2024-06-15T10:00:00",
  "next_task": {{
    "agent": "Visuals Agent",
    "task": "Design matching visuals for two post variants for social campaign.",
    "priority": 2
  }}
}}
"""
        try:
            post_data = interpret_command(prompt, self.client_id)
            log_action("Socials Agent", f"[POST_PLAN] {post_data}", self.client_id)

            post_1 = post_data.get("post_1", {})
            post_2 = post_data.get("post_2", {})
            recommended_time = post_data.get("recommended_time", str(datetime.now()))
            platforms = post_data.get("platforms", ["Instagram", "LinkedIn"])

            # Simulate posting (integration with actual platform APIs in future)
            log_action("Socials Agent", f"[POSTING] Platforms: {platforms} | Caption A: {post_1} | Caption B: {post_2} | Time: {recommended_time}", self.client_id)
            self.save_last_post_date()

            # Collaboration trigger
            if "next_task" in post_data:
                update_task_queue(post_data["next_task"]["agent"], post_data["next_task"], self.client_id)

            increment_metric("campaigns_launched")

        except Exception as e:
            log_action("Socials Agent", f"[ERROR] During create_and_post_content: {e}", self.client_id)

    def auto_post_trigger(self):
        # === [FEATURE: AUTO POSTING ON SCHEDULE] ===
        now = datetime.now()
        if (now - self.last_post_date) >= timedelta(days=7):
            log_action("Socials Agent", "[AUTO_TRIGGER] Weekly auto-post triggered.", self.client_id)
            self.create_and_post_content()
        else:
            log_action("Socials Agent", "[AUTO_TRIGGER] Not due yet for auto post.", self.client_id)

# ==================== END SocialsAgent.py ====================
