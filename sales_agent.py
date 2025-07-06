import os
import json
import random
from datetime import datetime
from pathlib import Path
from core.digiman_core import log_action, update_task_queue
from core.metrics import metrics
from core.memory_store import load_memory
from gpt.gpt_router import interpret_command

class SalesAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.required_keys = ["TWILIO_SID", "TWILIO_TOKEN"]
        self.active = all(os.getenv(k) for k in self.required_keys)
        self.memory = load_memory(client_id)

    def run_task(self, task):
        log_action("Sales Agent", f"Running task: {task['task']}", self.client_id)

        try:
            decision = interpret_command(task["task"], self.client_id)
            log_action("Sales Agent", f"GPT decision: {decision}", self.client_id)
            self.log_reasoning(task["task"], decision)
            task.update(decision)
        except Exception as e:
            log_action("Sales Agent", f"GPT interpretation failed: {e}", self.client_id)

        if "call" in task["task"].lower():
            self.run_sales_call()
        elif "prep" in task["task"].lower():
            self.prepare_pitch()
        elif "follow up" in task["task"].lower():
            self.follow_up()

    def run_sales_call(self):
        if self.active:
            log_action("Sales Agent", "Real call simulated via Twilio", self.client_id)
            update_task_queue("Closer Agent", {"task": "Handle objection from live call", "priority": 2}, self.client_id)
        else:
            log_action("Sales Agent", "Mock sales call executed", self.client_id)
            update_task_queue("Closer Agent", {"task": "Mock objection handling", "priority": 2}, self.client_id)
            metrics["revenue_generated"] += 800

    def prepare_pitch(self):
        pains = [m["content"] for m in self.memory if any(k in m["content"].lower() for k in ["frustrated", "confused", "low revenue", "no leads"])]
        target = pains[-1] if pains else "small business owner struggling with lead generation"
        pitch = f"We understand you're a {target}. We've helped similar businesses 10x their outreach through AI."

        log_action("Sales Agent", f"Pitch generated: {pitch}", self.client_id)
        update_task_queue("Outreach Agent", {"task": f"Deliver pitch: {pitch}", "priority": 2}, self.client_id)

    def follow_up(self):
        message = "Hey! Just checking in. Any thoughts on our last conversation? We're excited to support your scale journey."
        update_task_queue("Email Agent", {"task": f"Send follow-up: {message}", "priority": 2}, self.client_id)
        log_action("Sales Agent", "Follow-up email queued", self.client_id)

    def log_reasoning(self, input_text, output_json):
        log_path = Path(f".digi/clients/{self.client_id}/gpt_reasons.log")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as f:
            f.write(f"[{datetime.now()}] INPUT: {input_text}\\nOUTPUT: {output_json}\\n\\n")

