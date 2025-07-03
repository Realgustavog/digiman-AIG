import os
import json
import logging
from core.memory_store import load_memory, save_memory
from core.digiman_core import update_task_queue, log_action
from datetime import datetime
from pathlib import Path
import openai

# === Setup ===
openai.api_key = os.getenv("OPENAI_API_KEY")
logger = logging.getLogger("GPT_Router")

# === Semantic Memory Retrieval (future extendable) ===
def retrieve_relevant_memory(memory, query):
    # Placeholder for future semantic embedding retrieval
    # Currently selects last 10 items mentioning key terms
    key_terms = ["campaign", "lead", "client", "sales", "growth"]
    relevant = [m for m in memory if any(k in m.get("content", "").lower() for k in key_terms)]
    return relevant[-5:] if relevant else memory[-5:]

# === Interpret Command ===
def interpret_command(text_input, client_id="default"):
    memory = load_memory(client_id)
    relevant_memory = retrieve_relevant_memory(memory, text_input)

    business_phase = "growth"  # Future dynamic phase detection
    seasonality = "Q3 planning"  # Future seasonal logic

    system_prompt = f"""
You are DigiMan, the Autonomous AI COO of a business, managing and routing tasks across agents with context awareness and precision.

Business Phase: {business_phase}
Seasonality: {seasonality}

Respond ONLY with a strict JSON object like:
{{
  "agent": "Marketing Agent",
  "task": "Create Instagram campaign targeting tech founders",
  "priority": 2,
  "self_improvement_task": {{
      "agent": "Manager Agent",
      "task": "Review routing strategy for better seasonal alignment",
      "priority": 1
  }}
}}

AFTER the JSON, provide a short reasoning for your decision.
"""

    messages = [{"role": "system", "content": system_prompt}]
    for m in relevant_memory:
        messages.append({"role": m.get("role", "user"), "content": m.get("content", "")})
    messages.append({"role": "user", "content": text_input})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-preview",
            messages=messages,
            temperature=0.2
        )
        content = response.choices[0].message["content"]
        logger.info("GPT Raw Response: %s", content)

        split = content.split('}', 1)
        json_part = split[0] + "}" if "}" in split[0] else content
        reasoning = split[1].strip() if len(split) > 1 else ""

        try:
            parsed = json.loads(json_part)
            required_keys = {"agent", "task", "priority"}
            if required_keys.issubset(parsed.keys()):
                # Save to memory
                memory.append({"role": "user", "content": text_input})
                memory.append({"role": "assistant", "content": json_part})
                save_memory(client_id, memory)

                # Log reasoning
                log_path = Path(f".digi/clients/{client_id}/gpt_reasons.log")
                log_path.parent.mkdir(parents=True, exist_ok=True)
                with open(log_path, "a") as f:
                    f.write(f"[{datetime.now()}] INPUT: {text_input}\nDECISION: {json_part}\nREASONING: {reasoning}\n\n")

                # Handle optional self-improvement task
                if "self_improvement_task" in parsed:
                    update_task_queue(
                        parsed["self_improvement_task"]["agent"],
                        parsed["self_improvement_task"],
                        client_id
                    )
                    log_action(
                        "GPT Router",
                        f"Queued self-improvement task: {parsed['self_improvement_task']}",
                        client_id
                    )

                return parsed
            else:
                raise ValueError("Missing required keys in GPT response")
        except Exception as parse_error:
            logger.error("Failed to parse GPT response: %s", parse_error)
            return {
                "agent": "Manager Agent",
                "task": f"Fallback routing from GPT parse fail on: {text_input}",
                "priority": 1
            }

    except Exception as e:
        logger.error("GPT interpretation error: %s", str(e))
        return {
            "agent": "Manager Agent",
            "task": f"Unable to interpret: {text_input}",
            "priority": 1
        }
