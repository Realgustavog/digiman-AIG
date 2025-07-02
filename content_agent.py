# Logic for Content Agent
from pathlib import Path

# Define path for content_agent.py
content_agent_path = Path("/mnt/data/content_agent.py")

content_agent_code = '''
import json
from pathlib import Path
from datetime import datetime, timedelta
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from gpt.gpt_router import interpret_command

class ContentAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.content_dir = Path(f".digi/clients/{client_id}/content")
        self.content_dir.mkdir(parents=True, exist_ok=True)
        self.calendar_file = self.content_dir / "content_calendar.json"
        if not self.calendar_file.exists():
            self.calendar_file.write_text(json.dumps([], indent=2))

    def run_task(self, task):
        log_action("Content Agent", f"Running task: {task['task']}", self.client_id)
        command = task["task"].lower()

        try:
            gpt = interpret_command(task["task"], self.client_id)
            log_action("Content Agent", f"GPT Decision: {gpt}", self.client_id)
            task.update(gpt)
        except Exception as e:
            log_action("Content Agent", f"GPT failed: {e}", self.client_id)

        if "generate content" in command or "write" in command:
            self.generate_content(task["task"])
        elif "recycle" in command:
            self.repurpose_content()
        elif "lead magnet" in command:
            self.create_lead_magnet()
        elif "auto" in command:
            self.auto_publish()

    def generate_content(self, topic):
        context = "\\n".join([m["content"] for m in self.memory[-5:] if m.get("role") == "user"])
        prompt = f"""
You are an AI Content Strategist. Write content for: {topic}.
Format: newsletter, blog, or video script (choose).
Tone: Match previous memory.
Add SEO keywords, CTA, and metadata.
"""

        draft = interpret_command(prompt, self.client_id).get("task", "Draft pending...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = self.content_dir / f"draft_{timestamp}.txt"
        filename.write_text(draft)

        log_action("Content Agent", f"Saved draft: {filename.name}", self.client_id)

        # Send to other agents
        update_task_queue("Visuals Agent", {"task": f"Design visuals for: {topic}", "priority": 2}, self.client_id)
        update_task_queue("Socials Agent", {"task": f"Schedule content post: {topic}", "priority": 2}, self.client_id)
        update_task_queue("Marketing Agent", {"task": f"Include in campaign: {topic}", "priority": 1}, self.client_id)

        self.log_calendar(topic, filename.name)

    def repurpose_content(self):
        drafts = list(self.content_dir.glob("draft_*.txt"))
        if not drafts:
            log_action("Content Agent", "No content to recycle", self.client_id)
            return
        last = drafts[-1].read_text()
        reprompt = f"Convert this into a tweet thread and IG caption:\\n{last}"
        short = interpret_command(reprompt, self.client_id).get("task", "")
        filename = self.content_dir / f"recycled_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        filename.write_text(short)
        log_action("Content Agent", f"Recycled into: {filename.name}", self.client_id)

    def create_lead_magnet(self):
        prompt = "Write a 1-page PDF lead magnet for our product, including value props and CTA."
        pdf_draft = interpret_command(prompt, self.client_id).get("task", "")
        filename = self.content_dir / f"lead_magnet_{datetime.now().strftime('%Y%m%d')}.txt"
        filename.write_text(pdf_draft)
        log_action("Content Agent", f"Created lead magnet: {filename.name}", self.client_id)

    def auto_publish(self):
        last_publish = self.get_last_publish_date()
        now = datetime.now()
        if not last_publish or (now - last_publish).days >= 7:
            self.generate_content("Weekly auto content drop")

    def log_calendar(self, title, file):
        log = json.loads(self.calendar_file.read_text())
        log.append({
            "title": title,
            "file": file,
            "timestamp": datetime.now().isoformat()
        })
        self.calendar_file.write_text(json.dumps(log, indent=2))

    def get_last_publish_date(self):
        log = json.loads(self.calendar_file.read_text())
        if not log:
            return None
        last = sorted(log, key=lambda x: x["timestamp"])[-1]
        return datetime.fromisoformat(last["timestamp"])
'''

# Save file
content_agent_path.write_text(content_agent_code.strip())

str(content_agent_path)
