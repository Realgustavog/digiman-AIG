# Executes autonomous task loop
from pathlib import Path

# Path to save the autonomous_loop.py
autonomous_loop_path = Path("/mnt/data/autonomous_loop.py")

# Full autonomous loop logic
autonomous_loop_code = '''
import time
from core.agent_loader import load_agents
from core.digiman_core import log_action
from core.memory_store import load_memory
from core.metrics import metrics
from core.digiman_core import update_task_queue, load_task_queue
from datetime import datetime

def run_autonomous_loop(client_id=None):
    agents = load_agents(client_id=client_id)
    queue = load_task_queue(client_id)

    for agent_name, agent_class in agents.items():
        agent_instance = agent_class(client_id=client_id)
        agent_tasks = sorted(queue.get(agent_name, []), key=lambda x: x.get("priority", 1), reverse=True)

        for task in agent_tasks:
            try:
                agent_instance.run_task(task)
            except Exception as e:
                log_action(agent_name, f"Task error: {e}", client_id)
                metrics["tasks_failed"] += 1

        # Clear queue after run
        queue[agent_name] = []

    # Log loop completion
    log_action("Autonomous Loop", f"Completed run for client: {client_id}", client_id)

    return True

def loop_forever(interval_seconds=10, client_id=None):
    while True:
        run_autonomous_loop(client_id)
        time.sleep(interval_seconds)
'''

# Save the file
autonomous_loop_path.write_text(autonomous_loop_code.strip())

str(autonomous_loop_path)
