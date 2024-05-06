## GPT-Chatbot

This demo showcases how to use the OpenAI API's function calls and other third-party services & APIs to customize your chatbot.

### Features & Tricks

- Basic usage of the OpenAI API and function calls
- Streaming output for both chat and function calls
- Front-end page setup
- Integration with third-party APIs


### Explaination

Although there are many resources explaining how to use the OpenAI API and function calls, such as [How to call functions with chat model](https://cookbook.openai.com/examples/how_to_call_functions_with_chat_models), [How to call functions for knowledge retrieval](https://cookbook.openai.com/examples/how_to_call_functions_for_knowledge_retrieval), I found some points to be confusing for beginners and some aspects difficult to grasp. Therefore, I built this demo with some fun features and also addressed some common issues.

This demo contains two part:
- The first part is a teminal application, you can modify `chatbot.py` and `functions.py` and run `main.py` to see changes.
- The second part is a web front-end page, involving files such as `functions.py` and `app.py`, which we will introduce later.


### Usage

For the first part, run the following command in your teminal:

```python
python main.py
```

For the second part, run the following command in your teminal:

```python
flask run
```


#### Basic usage of OpenAI API and function call

To get started, please set up your OpenAI API key in the `API_KEY` field within the `.env` file.

`chatbot.py` provides a basic version to help you understand how the OpenAI API function call works.

Please note that some related parameters have changed. Refer to the https://platform.openai.com/docs/api-reference/chat/create to find more details.


#### Streaming output for both chat and function calls

Here I solved a problem.

To achieve quicker and more natural displays, I chose to streaming the respones. However, it's cannot work straightforwardly for function call, becase function call returns you the function name with parameters need to be executed, and you do not want to show this to users.

You can find a solution in the `generate()` function within `app.py`, which is also involves repeatly using function calls - pass the results of a function call back to GPT, which then organizes the respone or makes further function calls.


#### Front-end page setup

You can find the template of the front-end page on: https://github.com/openai/openai-quickstart-python/tree/master/examples/chat-basic.


#### Integration with third-party APIs

We have used two third-party APIs in this demo - [Weather API](https://www.weatherapi.com/docs/) and [Serpapi](https://serpapi.com/).

You can setup your API keys in the `SERPAPI_KEY` and `WEATHER_API` fields within the `.env` file. 