from chatbot import chatbot

prompt = """
Query weather for users based on location provided.

Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.
"""

message = [
    {
        "role": "system",
        "content": prompt,
    }
]


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                },
                "required": ["location", "format"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_past_n_day_weather",
            "description": "Get past N-day's weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                    "num_days": {
                        "type": "integer",
                        "description": "The number of past days",
                    }
                },
                "required": ["location", "format", "num_days"]
            },
        }
    },
]


content = input("\n********************************\nUser: \n")
while content != 'Finish':
    message.append({"role": "user", "content": content})
    reply = chatbot(messages=message, tools=tools)
    
    msg = ''
    for i in reply:
        print(i, end='', flush=True)
        msg += i
    message.append({'role': 'assistant', 'content': msg})
    
    content = input("\n********************************\nUser: \n")