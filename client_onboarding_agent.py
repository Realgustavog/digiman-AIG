from pathlib import Path

# Define path for fully enhanced client_onboarding_agent.py
enhanced_onboarding_path = Path("/mnt/data/client_onboarding_agent.py")

correct_enhanced_onboarding_code = '''
import os
import json
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from pathlib import Path
from gpt.gpt_router import interpret_command
from datetime import datetime

class ClientOnboardingAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.client_path = f".digi/clients/{client_id}"
        self.memory_file = os.path.join(self.client_path, "memory.json")
        self.queue_file = os.path.join(self.client_path, "agent_queue.json")
        self.memory = load_memory(client_id)
        self.default_agents_by_tier = {
            "starter": ["Manager Agent", "Email Agent", "CRM Agent", "Support Agent", "WebBuilder Agent"],
            "pro": ["Marketing Agent", "Analyst Agent", "Socials Agent", "Sales Agent"],
            "enterprise": [
                "Content Agent", "Visuals Agent", "Outreach Agent", "Subscription Agent",
                "Closer Agent", "Financial Allocation Agent", "Monetization Agent",
                "Autonomous Sales Replicator", "Franchise Builder Agent", "Franchise Intelligence Agent",
                "Franchise Relationship Agent", "Tutorial Agent", "Scout Agent", "Partnership Scout Agent",
                "Client Onboarding Agent"
            ]
        }

    def run_task(self, task):
        log_action("Client Onboarding Agent", f"Running task: {task['task']}", self.client_id)

        try:
            gpt_decision = interpret_command(task["task"], self.client_id)
            log_action("Client Onboarding Agent", f"GPT interpreted onboarding task: {gpt_decision}", self.client_id)
            self.log_reasoning(task["task"], gpt_decision)
            task.update(gpt_decision)
        except Exception as e:
            log_action("Client Onboarding Agent", f"GPT failed to parse: {e}", self.client_id)

        if "onboard" in task["task"].lower():
            plan = task.get("plan", "starter").lower()
            self.setup_client_storage()
            self.assign_subscription(plan)
            self.activate_default_agents(plan)
            self.seed_initial_tasks(plan)
            log_action("Client Onboarding Agent", f"Onboarding complete for plan: {plan}", self.client_id)

    def setup_client_storage(self):
        os.makedirs(self.client_path, exist_ok=True)
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w") as f:
                json.dump([], f)
        if not os.path.exists(self.queue_file):
            with open(self.queue_file, "w") as f:
                json.dump({}, f)

    def assign_subscription(self, plan):
        sub_path = os.path.join(self.client_path, "subscription.json")
        with open(sub_path, "w") as f:
            json.dump({"plan": plan}, f, indent=2)
        log_action("Client Onboarding Agent", f"Assigned subscription: {plan}", self.client_id)

    def activate_default_agents(self, plan):
        active_agents = []
        for tier in ["starter", "pro", "enterprise"]:
            if tier == "starter" or (tier == "pro" and plan != "starter") or (tier == "enterprise" and plan == "enterprise"):
                active_agents += self.default_agents_by_tier[tier]
        log_action("Client Onboarding Agent", f"Activated agents: {', '.join(active_agents)}", self.client_id)

    def seed_initial_tasks(self, plan):
        tiers_to_load = ["starter"]
        if plan in ["pro", "enterprise"]:
            tiers_to_load.append("pro")
        if plan == "enterprise":
            tiers_to_load.append("enterprise")

        for tier in tiers_to_load:
            for agent in self.default_agents_by_tier[tier]:
                update_task_queue(agent, {"task": "Initiate onboarding action", "priority": 2}, self.client_id)

    def log_reasoning(self, input_text, output_json):
        log_path = Path(f".digi/clients/{self.client_id}/gpt_reasons.log")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as f:
            f.write(f"[{datetime.now()}] INPUT: {input_text}\\nOUTPUT: {output_json}\\n\\n")
'''

# Save the correct enhanced version
enhanced_onboarding_path.write_text(correct_enhanced_onboarding_code.strip())

str(enhanced_onboarding_path)
