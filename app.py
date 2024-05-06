from flask import (
    Flask,
    render_template,
    request,
    Response,
    stream_with_context,
    jsonify,
)
import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')

os.environ["OPENAI_API_KEY"] = API_KEY
client = OpenAI(
    api_key = os.environ.get(
        API_KEY),
)

from functions import get_current_weather, get_past_n_day_weather, call_google



app = Flask(__name__)


prompt = """You are a helpful assistant.

Query weather based on location provided, or answer user's questions based on the information provided.

Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.
"""

chat_history = [
    {"role": "system", "content": prompt},
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
    {
        "type": "function",
        "function": {
            "name": "call_google",
            "description": "Use the Google Chrome search information when you need to answer questions about current events or something you are not sure",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "User's query for you to answer for",
                    },
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                },
                "required": ["query"],
            },
        }
    },
]


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", chat_history=chat_history)


@app.route("/chat", methods=["POST"])
def chat():
    content = request.json["message"]
    chat_history.append({"role": "user", "content": content})
    return jsonify(success=True)


@app.route("/stream", methods=["GET"])
def stream():
    def generate():
        flag = True
        while flag:
            assistant_response_content = ""
            
            response = client.chat.completions.create(
                model='gpt-4-turbo',
                messages=chat_history,
                stream=True,
                tools=tools,
                tool_choice=None
            )
            
            func_calls = []
            fc = None
            
            function_call_detected = False
            
            for response_chunk in response:
                if response_chunk.choices:
                    deltas = response_chunk.choices[0].delta
                    
                    if deltas.tool_calls:
                        function_call_detected = True
                        if deltas.tool_calls[0].function.name:
                            if not fc:
                                fc = {'name': None, 'arguments': ''}
                            else:
                                func_calls.append(fc)
                                fc = {'name': None, 'arguments': ''}
                            fc["name"] = deltas.tool_calls[0].function.name
                        if deltas.tool_calls[0].function.arguments:
                            fc["arguments"] += deltas.tool_calls[0].function.arguments
                    if (
                        function_call_detected
                        and response_chunk.choices[0].finish_reason == "tool_calls"
                    ):
                        func_calls.append(fc)
                        
                        for i in func_calls:
                            if i['name'] == 'get_current_weather':
                                result = get_current_weather(location=json.loads(i['arguments'])['location'], unit=json.loads(i['arguments'])['format'])
                                reply = 'Currently, the temperature is: ' + str(result) + f" {json.loads(i['arguments'])['format']}"
                                chat_history.append(
                                    {
                                        "role": "function",
                                        "name": 'get_current_weather',
                                        "content": reply,
                                    }
                                )

                            elif i['name'] == 'get_past_n_day_weather':
                                result = get_past_n_day_weather(location=json.loads(i['arguments'])['location'], unit=json.loads(i['arguments'])['format'], days=json.loads(i['arguments'])['num_days'])
                                chat_history.append(
                                    {
                                        "role": "function",
                                        "name": 'get_past_n_day_weather',
                                        "content": result,
                                    }
                                )

                            elif i['name'] == 'call_google':
                                result = call_google(**json.loads(i['arguments']))
                                
                                chat_history.append(
                                    {
                                        "role": "function",
                                        "name": 'call_google',
                                        "content": result,
                                    }
                                )
                        # print(chat_history)
                    elif deltas.content and not function_call_detected:
                        flag = False
                        assistant_response_content += deltas.content
                        yield f"data: {deltas.content}\n\n"
                    if response_chunk.choices[0].finish_reason == "stop":
                        break
            
            # Once the loop is done, append the full message to chat_history
            chat_history.append(
                {"role": "assistant", "content": assistant_response_content}
            )

    return Response(stream_with_context(generate()), mimetype="text/event-stream")


@app.route("/reset", methods=["POST"])
def reset_chat():
    global chat_history
    chat_history = [{"role": "system", "content": prompt}]
    return jsonify(success=True)
