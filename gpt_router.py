import openai
import os
import json
import logging
from core.memory_store import load_memory, save_memory
from pathlib import Path
from datetime import datetime

openai.api_key = os.getenv("OPENAI_API_KEY")
logger = logging.getLogger("GPT_Router")

def interpret_command(text_input, client_id="default"):
    memory = load_memory(client_id)
    context_messages = [
        {"role": "system", "content": "You are DigiMan, the AI COO of a business. You interpret user input and respond ONLY with a JSON object like: {'agent': '...', 'task': '...', 'priority': 1-3}. Also include a second message to yourself AFTER the JSON explaining WHY you chose that agent and task."}
    ]
    for m in memory[-5:]:
        context_messages.append(m)

    context_messages.append({"role": "user", "content": text_input})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=context_messages,
            temperature=0.2
        )
        content = response.choices[0].message["content"]
        logger.info("GPT Raw Response: %s", content)

        split = content.split('}', 1)
        json_part = split[0] + "}" if "}" in split[0] else content
        reasoning = split[1].strip() if len(split) > 1 else ""

        try:
            parsed = json.loads(json_part)
            if all(k in parsed for k in ["agent", "task", "priority"]):
                memory.append({"role": "user", "content": text_input})
                memory.append({"role": "assistant", "content": json_part})
                save_memory(client_id, memory)

                log_path = Path(f".digi/clients/{client_id}/gpt_reasons.log")
                log_path.parent.mkdir(parents=True, exist_ok=True)
                with open(log_path, "a") as f:
                    f.write(f"[{datetime.now()}] INPUT: {text_input}\nDECISION: {json_part}\nREASON: {reasoning}\n\n")

                return parsed
            else:
                raise ValueError("Missing keys in GPT response")
        except Exception as parse_error:
            logger.error("Failed to parse GPT response: %s", parse_error)
            return {
                "agent": "Manager Agent",
                "task": f"Default fallback task from: {text_input}",
                "priority": 1
            }

    except Exception as e:
        logger.error("GPT interpretation error: %s", str(e))
        return {
            "agent": "Manager Agent",
            "task": f"Unable to interpret: {text_input}",
            "priority": 1
        }
