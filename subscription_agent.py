# ==================== subscription_agent.py (DigiMan OS) ====================

import json
import os
from datetime import datetime
from pathlib import Path
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from core.metrics import increment_metric
from gpt.gpt_router import interpret_command

class SubscriptionAgent:
    def __init__(self, client_id=None):
        # [INIT]
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.subscription_file = Path(f".digi/clients/{client_id}/subscription.json")
        self.subscription = self.load_subscription()
        self.available_plans = {
            "starter": {"price": 29, "features": ["Email", "CRM", "Support", "WebBuilder"]},
            "pro": {"price": 99, "features": ["Marketing", "Analyst", "Socials", "Sales"]},
            "enterprise": {"price": 249, "features": ["Advanced Agents", "Franchise", "Custom AI"]}
        }

    def load_subscription(self):
        if self.subscription_file.exists():
            return json.loads(self.subscription_file.read_text())
        else:
            sub = {"plan": "starter", "renewal_date": datetime.now().isoformat()}
            self.save_subscription(sub)
            return sub

    def save_subscription(self, sub):
        self.subscription_file.parent.mkdir(parents=True, exist_ok=True)
        self.subscription_file.write_text(json.dumps(sub, indent=2))

    def run_task(self, task):
        log_action("Subscription Agent", f"[RUN_TASK] {task['task']}", self.client_id)
        increment_metric("tasks_processed")

        try:
            gpt_decision = interpret_command(task["task"], self.client_id)
            log_action("Subscription Agent", f"[GPT_DECISION] {gpt_decision}", self.client_id)
            task.update(gpt_decision)
        except Exception as e:
            log_action("Subscription Agent", f"[ERROR] GPT interpretation failed: {e}", self.client_id)

        if "upgrade" in task["task"].lower() or "downgrade" in task["task"].lower():
            self.handle_plan_change(task)
        elif "renew" in task["task"].lower() or "subscription" in task["task"].lower():
            self.process_renewal()
        elif "cancel" in task["task"].lower():
            self.cancel_subscription()

    def handle_plan_change(self, task):
        # [FEATURE: GPT-GUIDED PLAN CHANGE]
        prompt = f"""
You are the Subscription Agent for DigiMan OS.

Analyze the client's current usage:
{json.dumps(self.subscription, indent=2)}

Recent memory:
{" ".join([m["content"] for m in self.memory[-5:] if isinstance(m, dict)])}

Recommend whether the client should upgrade, downgrade, or remain on their current plan.
If upgrading, suggest a plan and reason.

Respond in JSON:
{{
  "recommendation": "upgrade" | "downgrade" | "stay",
  "suggested_plan": "pro",
  "reason": "Client is using advanced features and needs more agent slots."
}}
"""
        try:
            recommendation = interpret_command(prompt, self.client_id)
            log_action("Subscription Agent", f"[PLAN_RECOMMENDATION] {recommendation}", self.client_id)

            action = recommendation.get("recommendation", "stay")
            suggested_plan = recommendation.get("suggested_plan", self.subscription["plan"])

            if action == "upgrade" and suggested_plan in self.available_plans:
                self.subscription["plan"] = suggested_plan
                self.subscription["renewal_date"] = datetime.now().isoformat()
                self.save_subscription(self.subscription)
                increment_metric("revenue_generated", self.available_plans[suggested_plan]["price"])
                update_task_queue("Manager Agent", {
                    "task": f"Client upgraded to {suggested_plan}. Activate relevant agents.",
                    "priority": 2
                }, self.client_id)
                log_action("Subscription Agent", f"Upgraded client to {suggested_plan}.", self.client_id)

            elif action == "downgrade":
                self.subscription["plan"] = suggested_plan
                self.subscription["renewal_date"] = datetime.now().isoformat()
                self.save_subscription(self.subscription)
                update_task_queue("Manager Agent", {
                    "task": f"Client downgraded to {suggested_plan}. Adjust agents accordingly.",
                    "priority": 2
                }, self.client_id)
                log_action("Subscription Agent", f"Downgraded client to {suggested_plan}.", self.client_id)

            else:
                log_action("Subscription Agent", "No plan change needed at this time.", self.client_id)

        except Exception as e:
            log_action("Subscription Agent", f"[ERROR] Plan change failed: {e}", self.client_id)

    def process_renewal(self):
        # [FEATURE: AUTO-RENEWAL LOGIC]
        self.subscription["renewal_date"] = datetime.now().isoformat()
        self.save_subscription(self.subscription)
        increment_metric("revenue_generated", self.available_plans[self.subscription["plan"]]["price"])
        log_action("Subscription Agent", f"Subscription renewed for plan: {self.subscription['plan']}", self.client_id)

    def cancel_subscription(self):
        # [FEATURE: CANCELLATION HANDLING]
        self.subscription["plan"] = "cancelled"
        self.subscription["renewal_date"] = datetime.now().isoformat()
        self.save_subscription(self.subscription)
        log_action("Subscription Agent", "Subscription cancelled by client request.", self.client_id)
        update_task_queue("Support Agent", {
            "task": "Follow up with client on cancellation to gather feedback and attempt recovery.",
            "priority": 2
        }, self.client_id)

# ==================== END subscription_agent.py ====================

