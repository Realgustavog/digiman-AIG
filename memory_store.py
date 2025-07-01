import json
from pathlib import Path

def load_memory(client_id):
    path = Path(f".digi/clients/{client_id}/memory.json")
    if path.exists():
        return json.loads(path.read_text())
    return []

def save_memory(client_id, messages):
    path = Path(f".digi/clients/{client_id}/memory.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(messages, indent=2))