import openai
from tenacity import retry, wait_random_exponential, stop_after_attempt
import json

GPT_MODEL = "gpt-3.5-turbo"

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

# openai.api_key = open('./key.txt', 'r').read().strip('\n')

client = openai.OpenAI(api_key=open('./key.txt', 'r').read().strip('\n'))

messages = []
messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
messages.append({"role": "user", "content": "What's the weather like today"})
chat_response = chat_completion_request(
    messages
)
# print(chat_response)
assistant_message = chat_response.choices[0].message
messages.append(assistant_message)
print(assistant_message)