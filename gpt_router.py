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
        {"role": "system", "content": "You are DigiMan, the AI COO of a business."}
    ]
    for m in memory[-5:]:  # Limit to last 5 messages for prompt efficiency
        context_messages.append(m)

    context_messages.append({"role": "user", "content": text_input})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=context_messages,
            temperature=0.3
        )
        reply = response.choices[0].message["content"]
        logger.info("GPT Response: %s", reply)

        # Try to parse the reply as JSON
        parsed = json.loads(reply)
        memory.append({"role": "user", "content": text_input})
        memory.append({"role": "assistant", "content": reply})
        save_memory(client_id, memory)

        return parsed

    except Exception as e:
        logger.error("GPT interpretation error: %s", str(e))
        return {
            "agent": "Manager Agent",
            "task": f"Unable to interpret: {text_input}",
            "priority": 1
        }