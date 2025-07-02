# Logic for Sales Agent
import json
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from pathlib import Path
from gpt.gpt_router import interpret_command

class SalesAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.pricing = self.load_pricing()
        self.emotion_cues = {
            "i'm new": "DigiMan was built for people just like you. No experience needed.",
            "first time": "That’s perfect — our system is built to onboard you instantly.",
            "overwhelmed": "Let DigiMan handle the operations. You just guide the vision.",
            "confused": "We’ll simplify it. You’ll never have to guess what to do next.",
            "expensive": "Compared to a full team or agency, DigiMan is a fraction of the cost.",
            "ai is scary": "That’s why DigiMan works like a team, not a tool. We manage it for you."
        }

    def run_task(self, task):
        log_action("Sales Agent", f"Running task: {task['task']}", self.client_id)

        try:
            gpt_decision = interpret_command(task["task"], self.client_id)
            log_action("Sales Agent", f"GPT interpreted task: {gpt_decision}", self.client_id)
            task.update(gpt_decision)
        except Exception as e:
            log_action("Sales Agent", f"GPT failed to interpret: {e}", self.client_id)

        if "close" in task["task"].lower() or "pitch" in task["task"].lower():
            self.deliver_pitch()

    def load_pricing(self):
        path = Path("pricing.json")
        if path.exists():
            return json.loads(path.read_text())
        return {}

    def deliver_pitch(self):
        user_messages = [m["content"].lower() for m in self.memory[-10:] if isinstance(m, dict) and m.get("role") == "user"]
        hooks = []

        for msg in user_messages:
            for cue in self.emotion_cues:
                if cue in msg:
                    hooks.append(self.emotion_cues[cue])

        pricing_lines = [f"{tier.title()} – ${info['price']}/mo\nIncludes: {', '.join(info['features'])}" for tier, info in self.pricing.items()]
        pricing_summary = "\n\n".join(pricing_lines)

        if hooks:
            message = "\n".join(hooks) + "\n\nHere’s what DigiMan offers:\n" + pricing_summary
        else:
            message = "Here’s what DigiMan offers:\n" + pricing_summary

        log_action("Sales Agent", f"Delivered pitch:\n{message}", self.client_id)
        update_task_queue("Closer Agent", {"task": "Follow up with warm lead and confirm tier", "priority": 3}, self.client_id)
