# Logic for Financial Allocation Agent
from pathlib import Path

# Define the full file path for the enhanced Financial Allocation Agent
financial_agent_path = Path("/mnt/data/financial_allocation_agent.py")

# Full complete code for Financial Allocation Agent
full_financial_agent_code = '''
import os
import json
from datetime import datetime
from pathlib import Path
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from core.metrics import metrics, increment_metric
from gpt.gpt_router import interpret_command

class FinancialAllocationAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.metrics = metrics
        self.log_file = Path(f".digi/clients/{client_id}/financial_decisions.log")

    def run_task(self, task):
        log_action("Financial Allocation Agent", f"Running task: {task['task']}", self.client_id)
        try:
            self.evaluate_allocation(task)
            increment_metric("tasks_processed")
        except Exception as e:
            log_action("Financial Allocation Agent", f"Task error: {e}", self.client_id)

    def evaluate_allocation(self, task):
        context_summary = "\\n".join([m["content"] for m in self.memory[-5:] if "content" in m])
        prompt = f"""
You are the Financial Allocation Agent for an AI-powered autonomous business system.

Objective:
- Maximize return on resource allocation (RoR, IRR, GRR)
- Collaborate with AnalystAgent, MonetizationAgent, ManagerAgent
- Balance stability, scale, and strategic focus

Metrics:
{json.dumps(self.metrics, indent=2)}

User Memory:
{context_summary}

Task:
{task['task']}

Evaluate:
- Task viability
- Expected return
- Financial phase fit
- Capital impact

Output format:
{{
  "decision": "approve" | "deny" | "delay",
  "allocated_amount": "$1200",
  "projected_RoR": "280%",
  "expected_IRR": "39%",
  "impact_summary": "Expected to increase MRR by $2,000",
  "collaboration": ["Analyst Agent", "Monetization Agent"],
  "next_task": {{
    "agent": "Marketing Agent",
    "task": "Launch funded campaign with $1200 budget targeting tech founders",
    "priority": 3
  }}
}}
"""
        try:
            result = interpret_command(prompt, self.client_id)
            decision = result.get("decision", "delay")
            summary = result.get("impact_summary", "No summary available")
            collaborators = ", ".join(result.get("collaboration", []))

            self.log_reasoning(prompt, result)

            log_action("Financial Allocation Agent", f"GPT Decision: {decision} | {summary} | Collab: {collaborators}", self.client_id)

            if decision == "approve" and "next_task" in result:
                update_task_queue(result["next_task"]["agent"], result["next_task"], self.client_id)

            elif decision == "delay":
                update_task_queue("Analyst Agent", {
                    "task": "Review forecast risk for delayed financial request",
                    "priority": 2
                }, self.client_id)

            elif decision == "deny":
                log_action("Financial Allocation Agent", "Denied allocation due to low ROI or misalignment", self.client_id)

        except Exception as e:
            log_action("Financial Allocation Agent", f"GPT evaluation error: {e}", self.client_id)

    def log_reasoning(self, prompt, result):
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, "a") as f:
            f.write(f"[{datetime.now()}] PROMPT: {prompt}\\nRESPONSE: {json.dumps(result, indent=2)}\\n\\n")


