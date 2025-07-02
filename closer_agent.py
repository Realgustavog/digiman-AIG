# Logic for Closer Agent
import json
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from pathlib import Path

class CloserAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.pricing = self.load_pricing()
        self.objections = {
            "i'm new": "No worries at all. We built DigiMan to be your AI team — even if you're brand new to this.",
            "first time": "That’s exactly why DigiMan is here. We'll walk you through every step.",
            "don't know": "You don’t need to. We handle the AI logic — you focus on results.",
            "losing money": "We can replace your ad spend with data-backed automation for faster returns.",
            "seo not working": "Our agents handle SEO, content, and promotion — hands off.",
            "no clients": "Let’s solve that. DigiMan is built to fill your pipeline automatically."
        }

    def run_task(self, task):
        log_action("Closer Agent", f"Running task: {task['task']}", self.client_id)
        if "close deal" in task["task"].lower():
            self.respond_to_closing_opportunity(task)

    def load_pricing(self):
        path = Path("pricing.json")
        if path.exists():
            return json.loads(path.read_text())
        return {}

    def respond_to_closing_opportunity(self, task):
        recent_clues = [m["content"].lower() for m in self.memory[-8:] if isinstance(m, dict) and m.get("role") == "user"]
        found_pain = []

        for clue in recent_clues:
            for key in self.objections:
                if key in clue:
                    found_pain.append(self.objections[key])

        pricing_summary = "\n".join([f"{tier.title()} - ${data['price']}/mo: {', '.join(data['features'])}" for tier, data in self.pricing.items()])

        if not found_pain:
            message = f"Our system starts at $29/month. Here’s the full pricing:\n{pricing_summary}"
        else:
            message = f"{' '.join(found_pain)}\n\nHere’s how our pricing breaks down:\n{pricing_summary}"

        log_action("Closer Agent", f"Delivered pricing and reassurance:\n{message}", self.client_id)
        update_task_queue("Subscription Agent", {"task": "Initiate payment link with selected plan", "priority": 3}, self.client_id)
