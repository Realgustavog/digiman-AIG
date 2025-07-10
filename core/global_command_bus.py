class GlobalCommandBus:
    def __init__(self):
        self.command_log = []
        self.agents = {
            'digiman': self.handle_digiman,
            'web_builder': self.handle_web_builder,
            'crm': self.handle_crm
        }

    def parse_command(self, user_input):
        """
        Basic natural language to structured command parsing.
        Will expand with OpenAI function calling or structured parsing in Phase 2.
        """
        user_input = user_input.lower()
        if "digiman" in user_input:
            return 'digiman', user_input
        elif "web builder" in user_input:
            return 'web_builder', user_input
        elif "crm" in user_input:
            return 'crm', user_input
        else:
            return None, user_input

    def route_command(self, user_input):
        agent_key, command_content = self.parse_command(user_input)
        if agent_key and agent_key in self.agents:
            response = self.agents[agent_key](command_content)
            self.log_event(agent_key, command_content, response)
            return response
        else:
            response = f"Command not recognized or no agent mapped: {user_input}"
            self.log_event('unknown', user_input, response)
            return response

    def log_event(self, agent, command, response):
        self.command_log.append({
            'agent': agent,
            'command': command,
            'response': response
        })

    def handle_digiman(self, command):
        # Placeholder: In production, route to Digiman API/agent
        return f"[Digiman executing]: {command}"

    def handle_web_builder(self, command):
        # Placeholder: In production, route to Web Builder Agent
        return f"[Web Builder executing]: {command}"

    def handle_crm(self, command):
        # Placeholder: In production, route to CRM Agent
        return f"[CRM executing]: {command}"


if __name__ == "__main__":
    gcb = GlobalCommandBus()
    
    while True:
        user_input = input("\nEnter your command: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Exiting Global Command Bus.")
            break
        response = gcb.route_command(user_input)
        print(f"Response: {response}")
