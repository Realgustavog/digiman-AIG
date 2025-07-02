# Logic for Closer Agent
import json
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from pathlib import Path
from gpt.gpt_router import interpret_command

class CloserAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.pricing = self.load_pricing()
        self.objections = {
            "i'm new": "No worries at all. DigiMan was built for beginners. You’ll get full support.",
            "first time": "That’s exactly why we made this. We'll guide you step-by-step.",
            "don't know": "DigiMan simplifies it all — AI does the work, you get the results.",
            "losing money": "We'll turn your losses into predictable revenue with automated sales.",
            "seo failing": "Our agents handle SEO, outreach, and lead conversion for you.",
            "no clients": "Our job is to fix that. DigiMan generates, qualifies, and closes leads."
        }

    def run_task(self, task):
        log_action("Closer Agent", f"Running task: {task['task']}", self.client_id)

        try:
            gpt_decision = interpret_command(task["task"], self.client_id)
            log_action("Closer Agent", f"GPT interpreted task: {gpt_decision}", self.client_id)
            task.update(gpt_decision)
        except Exception as e:
            log_action("Closer Agent", f"GPT failed to interpret: {e}", self.client_id)

        if "close deal" in task["task"].lower():
            self.respond_to_closing_opportunity(task)

    def load_pricing(self):
        path = Path("pricing.json")
        if path.exists():
            return json.loads(path.read_text())
        return {}

    def respond_to_closing_opportunity(self, task):
        recent_clues = [m["content"].lower() for m in self.memory[-10:] if isinstance(m, dict) and m.get("role") == "user"]
        responses = []

        for clue in recent_clues:
            for key in self.objections:
                if key in clue:
                    responses.append(self.objections[key])

        pricing_summary = "\n".join([f"{tier.title()} – ${data['price']}/mo: {', '.join(data['features'])}" for tier, data in self.pricing.items()])

        if responses:
            message = "\n".join(responses) + "\n\nHere’s what we offer:\n" + pricing_summary
        else:
            message = "Let me break down our pricing for you:\n" + pricing_summary

        log_action("Closer Agent", f"Sent final pitch:\n{message}", self.client_id)
        update_task_queue("Subscription Agent", {"task": "Initiate payment link", "priority": 3}, self.client_id)
