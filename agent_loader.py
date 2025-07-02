# Dynamically loads agents from /agents/
# Rebuild agent_loader.py with GPT reasoning logging and prep for future improvements
from pathlib import Path

agent_loader_path = Path("/mnt/data/agent_loader.py")

fixed_agent_loader_code = '''
import os
import importlib.util
from pathlib import Path
import inspect
from core.digiman_core import evaluate_agent_quality, log_action
from gpt.gpt_router import interpret_command
from datetime import datetime

AGENT_REGISTRY = {}

def wrap_with_gpt(agent_class):
    class GPTWrappedAgent(agent_class):
        def run_task(self, task):
            log_action(self.__class__.__name__, f"Received task: {task['task']}", self.client_id)
            try:
                decision = interpret_command(task["task"], self.client_id)
                log_action(self.__class__.__name__, f"GPT-decided: {decision}", self.client_id)
                self.log_reasoning(task["task"], decision)
                task.update(decision)
            except Exception as e:
                log_action(self.__class__.__name__, f"GPT failed: {e}", self.client_id)
            super().run_task(task)

        def log_reasoning(self, input_text, output_json):
            log_path = Path(f".digi/clients/{self.client_id}/gpt_reasons.log")
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, "a") as f:
                f.write(f"[{datetime.now()}] INPUT: {input_text}\\nOUTPUT: {output_json}\\n\\n")

    return GPTWrappedAgent

def load_agents(agent_dir="agents", client_id=None):
    agent_path = Path(agent_dir)
    for file in agent_path.glob("*.py"):
        if file.name.startswith("_"):
            continue

        module_name = file.stem
        file_path = str(file.resolve())

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if name.endswith("Agent"):
                    code = inspect.getsource(obj)
                    score, reasons = evaluate_agent_quality(code)
                    if score >= 3:
                        wrapped_class = wrap_with_gpt(obj)
                        AGENT_REGISTRY[name.replace("Agent", " Agent")] = wrapped_class
                        log_action(name, f"Loaded (GPT-wrapped) agent with score {score}/4", client_id)
                    else:
                        log_action(name, f"Skipped (score {score}/4): {' | '.join(reasons)}", client_id)
        except Exception as e:
            log_action("Agent Loader", f"Error loading {file.name}: {e}", client_id)

    return AGENT_REGISTRY
'''

# Save the updated agent_loader.py
agent_loader_path.write_text(fixed_agent_loader_code.strip())

str(agent_loader_path)
