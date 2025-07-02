# Dynamically loads agents from /agents/
import os
import importlib.util
from pathlib import Path
import inspect
from core.digiman_core import evaluate_agent_quality, log_action
from gpt.gpt_router import interpret_command  # GPT is available to inject

AGENT_REGISTRY = {}

def wrap_with_gpt(agent_class):
    class GPTWrappedAgent(agent_class):
        def run_task(self, task):
            log_action(self.__class__.__name__, f"Received task: {task['task']}", self.client_id)
            try:
                decision = interpret_command(task["task"], self.client_id)
                log_action(self.__class__.__name__, f"GPT-decided: {decision}", self.client_id)
                task.update(decision)
            except Exception as e:
                log_action(self.__class__.__name__, f"GPT failed: {e}", self.client_id)
            super().run_task(task)
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
