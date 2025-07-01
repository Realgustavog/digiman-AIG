# Logic for Client Onboarding Agent
import os
import json
from core.digiman_core import log_action, update_task_queue

class ClientOnboardingAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.client_path = f".digi/clients/{client_id}"
        self.memory_file = os.path.join(self.client_path, "memory.json")
        self.queue_file = os.path.join(self.client_path, "agent_queue.json")
        self.default_agents_by_tier = {
            "starter": ["Email Agent", "Support Agent"],
            "pro": ["Email Agent", "CRM Agent", "Marketing Agent"],
            "enterprise": ["Email Agent", "CRM Agent", "Marketing Agent", "Manager Agent", "Visuals Agent", "Closer Agent"]
        }

    def run_task(self, task):
        log_action("Client Onboarding Agent", f"Running task: {task['task']}", self.client_id)
        if "onboard" in task["task"].lower():
            plan = task.get("plan", "starter").lower()
            self.setup_client_storage()
            self.assign_subscription(plan)
            self.activate_default_agents(plan)
            self.seed_initial_tasks(plan)
            log_action("Client Onboarding Agent", f"Completed onboarding for plan: {plan}", self.client_id)

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
        active_agents = self.default_agents_by_tier.get(plan, [])
        log_action("Client Onboarding Agent", f"Activated agents: {', '.join(active_agents)}", self.client_id)

    def seed_initial_tasks(self, plan):
        active_agents = self.default_agents_by_tier.get(plan, [])
        for agent in active_agents:
            if agent == "Email Agent":
                update_task_queue(agent, {"task": "Send welcome email", "priority": 2}, self.client_id)
            elif agent == "Support Agent":
                update_task_queue(agent, {"task": "Initiate onboarding support chat", "priority": 1}, self.client_id)
            elif agent == "CRM Agent":
                update_task_queue(agent, {"task": "Import initial lead list", "priority": 2}, self.client_id)
            elif agent == "Marketing Agent":
                update_task_queue(agent, {"task": "Create welcome campaign", "priority": 2}, self.client_id)
            elif agent == "Closer Agent":
                update_task_queue(agent, {"task": "Schedule onboarding call", "priority": 3}, self.client_id)
            elif agent == "Manager Agent":
                update_task_queue(agent, {"task": "Begin KPI tracking for new client", "priority": 2}, self.client_id)
