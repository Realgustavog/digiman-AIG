import openai
import os
import json
import logging
from core.memory_store import load_memory, save_memory

openai.api_key = os.getenv("OPENAI_API_KEY")
logger = logging.getLogger("GPT_Router")

def interpret_command(text_input, client_id="default"):
    memory = load_memory(client_id)
    context_messages = [
        {"role": "system", "content": "You are DigiMan, the AI COO of a business. You interpret commands and decide the best agent, task and priority to complete that command in JSON format only. You do not explain your reasoning, only return a JSON object with keys: agent, task, priority."}
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
        reply = response.choices[0].message["content"]
        logger.info("GPT Response: %s", reply)

        try:
            parsed = json.loads(reply)
            if all(k in parsed for k in ["agent", "task", "priority"]):
                memory.append({"role": "user", "content": text_input})
                memory.append({"role": "assistant", "content": reply})
                save_memory(client_id, memory)
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
