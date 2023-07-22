import openai
from secret import keys
import json
import streamlit as st

_starter_prompt = """You are a helpful assistant that helps people with their daily tasks.
Every single response to the user must use Markdown for formatting to make it neat and readable. Use tables for data.
Do not duplicate data when formatting.
Emails must absolutely always use html for formatting.
Do not send emails unless explicitly told to do so by the user. The user my explicitly say the word "send".
Always let the user review the email before sending it and ask for confirmation.
Never ever make up or invent email addresses if you don't actually know the email address.
You can use multiple functions one after the other if you deem it necessary, before giving a final response.
Only repeat actions if it is necessary.
In your responses only include information that is relevant to the user's query.
"""


class Conversator:
    def __init__(self, functions: list):
        openai.api_key = keys.openai_key
        self.messages = []
        self.internal_messages = [{"role": "system", "content": _starter_prompt}]
        self.functions = {}
        for function in functions:
            self.functions[function.name] = function

    def process_msg(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        self.internal_messages.append({"role": "user", "content": msg})
        with st.spinner("Thinking..."):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=self.internal_messages,
                functions=list(map(lambda x: x.to_dict(), self.functions.values())),
                function_call="auto"
            )
        message = response["choices"][0]["message"]

        while message.get("function_call"):
            func_name = message["function_call"]["name"]
            func_args = json.loads(message["function_call"]["arguments"])
            with st.spinner(func_args["reason"]):
                message = self.call_function(func_name, func_args)

        self.messages.append(message)
        self.internal_messages.append(message)
        return message["content"]

    def call_function(self, name: str, args: dict):
        func = self.functions[name]
        func_result = func(args)
        self.internal_messages.append({"role": "function", "name": name, "content": func_result})
        message = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=self.internal_messages,
            functions=list(map(lambda x: x.to_dict(), self.functions.values())),
            function_call="auto"
        )
        message = message["choices"][0]["message"]
        return message


    def get_messages(self):
        return self.messages

    def reset(self):
        self.messages = []
        self.internal_messages = [{"role": "system", "content": _starter_prompt}]
