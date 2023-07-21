import openai
from secret import keys
import json
import streamlit as st

class Conversator:
    def __init__(self, functions: list):
        openai.api_key = keys.openai_key
        self.messages = []
        self.internal_messages = []
        self.functions = {}
        for function in functions:
            self.functions[function.name] = function

    def process_msg(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        self.internal_messages.append({"role": "user", "content": msg})
        with st.spinner("Thinking..."):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.internal_messages,
                functions=list(map(lambda x: x.to_dict(), self.functions.values())),
                function_call="auto"
            )
        message = response["choices"][0]["message"]

        if message.get("function_call"):
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
            model="gpt-3.5-turbo",
            messages=self.internal_messages,
        )
        message = message["choices"][0]["message"]
        return message


    def get_messages(self):
        return self.messages

    def reset(self):
        self.messages = []
        self.internal_messages = []
