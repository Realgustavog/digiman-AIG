# Logic for Outreach Agent
import json
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from pathlib import Path
from gpt.gpt_router import interpret_command

class OutreachAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.pricing = self.load_pricing()
        self.prospect_cues = {
            "no time": "DigiMan gives you back your time by automating the work of an entire team.",
            "no clients": "That’s exactly what DigiMan fixes — we fill your pipeline while you sleep.",
            "slow growth": "Let DigiMan accelerate your traction without extra effort.",
            "ads don't work": "We replace ad spend with outreach, content, and inbound automation.",
            "not enough leads": "DigiMan generates, scores, and books your leads — all hands off."
        }

    def run_task(self, task):
        log_action("Outreach Agent", f"Running task: {task['task']}", self.client_id)

        try:
            gpt_decision = interpret_command(task["task"], self.client_id)
            log_action("Outreach Agent", f"GPT interpreted task: {gpt_decision}", self.client_id)
            task.update(gpt_decision)
        except Exception as e:
            log_action("Outreach Agent", f"GPT failed to interpret: {e}", self.client_id)

        if "outreach" in task["task"].lower() or "warm lead" in task["task"].lower():
            self.generate_prospect_message()

    def load_pricing(self):
        path = Path("pricing.json")
        if path.exists():
            return json.loads(path.read_text())
        return {}

    def generate_prospect_message(self):
        pain_points = [m["content"].lower() for m in self.memory[-10:] if isinstance(m, dict) and m.get("role") == "user"]
        hooks = []

        for msg in pain_points:
            for cue in self.prospect_cues:
                if cue in msg:
                    hooks.append(self.prospect_cues[cue])

        pricing_lines = [f"{tier.title()} – ${info['price']}/mo: {', '.join(info['features'])}" for tier, info in self.pricing.items()]
        pricing_summary = "\n".join(pricing_lines)

        if hooks:
            message = "Here’s what we can do for you:\n" + "\n".join(hooks) + "\n\nOur pricing starts at $29/month:\n" + pricing_summary
        else:
            message = "DigiMan automates your business with AI agents. Pricing starts at just $29/month.\n" + pricing_summary

        log_action("Outreach Agent", f"Sent outreach message:\n{message}", self.client_id)
        update_task_queue("Sales Agent", {"task": "Follow up with engaged lead", "priority": 2}, self.client_id)
