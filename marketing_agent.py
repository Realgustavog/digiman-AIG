from pathlib import Path

# Define path for enhanced marketing_agent.py
marketing_agent_path = Path("/mnt/data/marketing_agent.py")

enhanced_marketing_code = '''
# Logic for Marketing Agent
import json
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from core.metrics import metrics
from gpt.gpt_router import interpret_command
from pathlib import Path
from datetime import datetime, timedelta

class MarketingAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.metrics = metrics
        self.leads_path = Path(f".digi/clients/{client_id}/leads.json")
        self.last_campaign_log = Path(f".digi/clients/{client_id}/last_campaign.json")
        self.leads = self.load_leads()

    def run_task(self, task):
        log_action("Marketing Agent", f"Running task: {task['task']}", self.client_id)

        try:
            gpt_decision = interpret_command(task["task"], self.client_id)
            log_action("Marketing Agent", f"GPT interpreted task: {gpt_decision}", self.client_id)
            self.log_reasoning(task["task"], gpt_decision)
            task.update(gpt_decision)
        except Exception as e:
            log_action("Marketing Agent", f"GPT interpretation failed: {e}", self.client_id)

        if "campaign" in task["task"].lower():
            self.propose_campaign()
        elif "auto" in task["task"].lower() or "weekly" in task["task"].lower():
            self.check_auto_trigger()

    def load_leads(self):
        if self.leads_path.exists():
            return json.loads(self.leads_path.read_text())
        return []

    def load_last_campaign_date(self):
        if self.last_campaign_log.exists():
            data = json.loads(self.last_campaign_log.read_text())
            return datetime.fromisoformat(data.get("last_run"))
        return datetime.min

    def save_last_campaign_date(self):
        self.last_campaign_log.parent.mkdir(parents=True, exist_ok=True)
        self.last_campaign_log.write_text(json.dumps({"last_run": datetime.now().isoformat()}, indent=2))

    def propose_campaign(self):
        target_industry = self.detect_common_industry() or "general SMBs"
        gpt_insight = interpret_command(f"Create a campaign targeting {target_industry}. Include headline, CTA, offer.", self.client_id)

        campaign_brief = {
            "audience": target_industry,
            "goal": "generate qualified leads",
            "channels": ["email", "instagram", "linkedin"],
            "budget": "$500",
            "headline": gpt_insight.get("task"),
            "cta": "Claim your free AI business audit now"
        }

        log_action("Marketing Agent", f"Proposed campaign: {campaign_brief}", self.client_id)

        update_task_queue("Financial Allocation Agent", {
            "task": f"Approve marketing campaign budget: {campaign_brief}",
            "priority": 2
        }, self.client_id)

        update_task_queue("Visuals Agent", {
            "task": f"Design campaign visuals for: {campaign_brief['headline']}",
            "priority": 2
        }, self.client_id)

        update_task_queue("Socials Agent", {
            "task": f"Schedule posts for: {campaign_brief['headline']} on {', '.join(campaign_brief['channels'])}",
            "priority": 2
        }, self.client_id)

        update_task_queue("Analyst Agent", {
            "task": f"Analyze expected performance for: {campaign_brief['headline']}",
            "priority": 1
        }, self.client_id)

        self.save_last_campaign_date()

    def detect_common_industry(self):
        industries = [lead.get("industry", "unknown") for lead in self.leads if "industry" in lead]
        if not industries:
            return None
        return max(set(industries), key=industries.count)

    def check_auto_trigger(self):
        last_run = self.load_last_campaign_date()
        now = datetime.now()
        if (now - last_run) >= timedelta(days=7):
            log_action("Marketing Agent", "Weekly auto-trigger activated", self.client_id)
            self.propose_campaign()
        else:
            log_action("Marketing Agent", "Auto-trigger not due yet", self.client_id)

    def log_reasoning(self, input_text, output_json):
        log_path = Path(f".digi/clients/{self.client_id}/gpt_reasons.log")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as f:
            f.write(f"[{datetime.now()}] INPUT: {input_text}\\nOUTPUT: {output_json}\\n\\n")
'''

# Save the enhanced marketing_agent.py
marketing_agent_path.write_text(enhanced_marketing_code.strip())

str(marketing_agent_path)

