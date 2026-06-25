import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class Agent:
    def __init__(self, model="gpt-4o", tools=None, dispatch=None, system_prompt=None, max_steps=10):
        self.client = OpenAI()
        self.model = model
        self.tools = tools if tools is not None else []
        self.dispatch = dispatch if dispatch is not None else {}
        self.system_prompt = system_prompt if system_prompt is not None else "You are a helpful assistant."
        self.max_steps = max_steps
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

    def need_request_accept(self, tool_name):
        for tool in self.tools:
            if tool["function"]["name"] == tool_name:
                return tool["function"]["request_accept"]
        return False
    
    def run(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        
        for _ in range(self.max_steps):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools
            )
            msg = response.choices[0].message
            
            if msg.tool_calls:
                self.messages.append(msg)  # Store the assistant message with tool calls before adding tool results
                for tool_call in msg.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    if tool_name in self.dispatch:
                        try:
                            request_accept = self.need_request_accept(tool_name)
                            if request_accept:
                                accepted = input(f"Cho phép chạy {tool_name}({tool_args})? [y/N] ")
                                if accepted.upper() == "Y":
                                    print(f"User accepted calling tool: {tool_name}")
                                else:
                                    # invalid input
                                    self.messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": "Người dùng từ chối thao tác này."})
                                    continue

                            print(f"Calling tool: {tool_name} with arguments: {tool_args}")
                            result = self.dispatch[tool_name](**tool_args)
                            print(f"Result from {tool_name}: {result}")
                            self.messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(result)})
                        except Exception as e:
                            print(f"Error calling tool {tool_name}: {e}")
                            self.messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": "Error: " + str(e)})
                    else:
                        print(f"Tool {tool_name} is not defined.")
                        self.messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": f"Tool {tool_name} is not defined."})
            else:
                print(f"Model response: {msg.content}")
                return msg.content
        
        return "Max steps reached without a final response."

