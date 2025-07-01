# Dynamically loads agents from /agents/
import os
import importlib.util
from pathlib import Path
import inspect
from core.digiman_core import evaluate_agent_quality, log_action

AGENT_REGISTRY = {}

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
                        AGENT_REGISTRY[name.replace("Agent", " Agent")] = obj
                        log_action(name, f"Loaded agent with score {score}/4", client_id)
                    else:
                        log_action(name, f"Skipped (score {score}/4): {' | '.join(reasons)}", client_id)
        except Exception as e:
            log_action("Agent Loader", f"Error loading {file.name}: {e}", client_id)

    return AGENT_REGISTRY
