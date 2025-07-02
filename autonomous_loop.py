# Executes autonomous task loop
import time
from core.agent_loader import load_agents
from core.digiman_core import log_action, update_task_queue, load_task_queue
from core.metrics import metrics
from gpt.gpt_router import interpret_command
from datetime import datetime

class AutonomousLoop:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.metrics = metrics

    def run(self):
        agents = load_agents(client_id=self.client_id)
        queue = load_task_queue(self.client_id)

        for agent_name, agent_class in agents.items():
            agent_instance = agent_class(client_id=self.client_id)
            agent_tasks = sorted(queue.get(agent_name, []), key=lambda x: x.get("priority", 1), reverse=True)

            for task in agent_tasks:
                try:
                    # Run GPT interpretation before execution
                    gpt_decision = interpret_command(task["task"], self.client_id)
                    task.update(gpt_decision)
                    log_action(agent_name, f"GPT interpreted task: {gpt_decision}", self.client_id)

                    # Execute agent logic
                    agent_instance.run_task(task)

                except Exception as e:
                    log_action(agent_name, f"Task error: {e}", self.client_id)
                    self.metrics["tasks_failed"] += 1

            queue[agent_name] = []

        log_action("Autonomous Loop", f"Completed loop run for client: {self.client_id}", self.client_id)
        return True

    def loop_forever(self, interval_seconds=10):
        while True:
            self.run()
            time.sleep(interval_seconds)
