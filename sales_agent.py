# Logic for Sales Agent
import json
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from pathlib import Path

class SalesAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.pricing = self.load_pricing()
        self.emotion_cues = {
            "i'm new": "We’ve helped countless first-time founders — DigiMan handles the hard parts for you.",
            "first time": "You don’t need experience. We provide the system. You provide the goal.",
            "overwhelmed": "Totally understand. DigiMan takes the chaos out of building your business.",
            "confused": "That's why we built an intuitive platform. We lead, you approve.",
            "too much": "Think of DigiMan as your team. You’re not doing this alone.",
            "stressed": "Let DigiMan remove your bottlenecks — so you can focus on results.",
            "expensive": "Compared to hiring, we’re pennies on the dollar — and you get 20+ agents."
        }

    def run_task(self, task):
        log_action("Sales Agent", f"Running task: {task['task']}", self.client_id)
        if "close" in task["task"].lower() or "pitch" in task["task"].lower():
            self.deliver_pitch()

    def load_pricing(self):
        path = Path("pricing.json")
        if path.exists():
            return json.loads(path.read_text())
        return {}

    def deliver_pitch(self):
        user_messages = [m["content"].lower() for m in self.memory[-10:] if isinstance(m, dict) and m.get("role") == "user"]
        emotional_responses = []

        for message in user_messages:
            for cue in self.emotion_cues:
                if cue in message:
                    emotional_responses.append(self.emotion_cues[cue])

        pricing_lines = [f"{tier.title()} – ${info['price']}/mo\nIncludes: {', '.join(info['features'])}" for tier, info in self.pricing.items()]
        pricing_summary = "\n\n".join(pricing_lines)

        if emotional_responses:
            message = "\n".join(emotional_responses) + "\n\nHere’s what DigiMan offers:\n" + pricing_summary
        else:
            message = "Here’s what DigiMan offers:\n" + pricing_summary

        log_action("Sales Agent", f"Delivered strategic pitch:\n{message}", self.client_id)
        update_task_queue("Closer Agent", {"task": "Follow up with warm lead and confirm tier", "priority": 3}, self.client_id)
