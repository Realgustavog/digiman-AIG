from pathlib import Path
import json
from pathlib import Path
from datetime import datetime

MAX_MEMORY = 100  # Limit memory to prevent overload

def load_memory(client_id):
    path = Path(f".digi/clients/{client_id}/memory.json")
    if path.exists():
        try:
            messages = json.loads(path.read_text())
            return messages[-MAX_MEMORY:]  # Trim if over limit
        except json.JSONDecodeError:
            return []
    return []

def save_memory(client_id, messages):
    path = Path(f".digi/clients/{client_id}/memory.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    # Truncate memory if over limit
    messages = messages[-MAX_MEMORY:]
    path.write_text(json.dumps(messages, indent=2))

def add_memory_entry(client_id, role, content):
    memory = load_memory(client_id)
    timestamp = datetime.now().isoformat()
    memory.append({"role": role, "content": content, "timestamp": timestamp})
    save_memory(client_id, memory)

def clear_memory(client_id):
    path = Path(f".digi/clients/{client_id}/memory.json")
    if path.exists():
        path.unlink()

