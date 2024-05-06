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

from functions import get_current_weather, get_past_n_day_weather



def chatbot(messages, tools=None, tool_choice=None, model="gpt-4-turbo", use_steam=True):

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=use_steam,
        tools=tools,
        tool_choice=tool_choice
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
                        yield '\nCurrently, the temperature is: ' + str(result) + f" {json.loads(i['arguments'])['format']} \n"
                    elif i['name'] == 'get_past_n_day_weather':
                        result = get_past_n_day_weather(location=json.loads(i['arguments'])['location'], unit=json.loads(i['arguments'])['format'], days=json.loads(i['arguments'])['num_days'])
                        yield result + '\n'
            elif deltas.content and not function_call_detected:
                yield deltas.content
            if response_chunk.choices[0].finish_reason == "stop":
                break
