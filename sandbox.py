# sandbox.py
import os
from dotenv import load_dotenv

load_dotenv()

SANDBOX_MODE = os.getenv("SANDBOX_MODE", "False").lower() == "true"

def sandbox_log(agent_name, action, client_id=None):
    if SANDBOX_MODE:
        from core.digiman_core import log_action
        log_action(agent_name, f"[SANDBOX MODE] {action}", client_id)
