import openai
from secret import keys
import json
import streamlit as st
import data.core as core
from src.gpt_function import GPTFunction
import yaml

unused_email_prompt = """Emails must absolutely always use html for formatting.
Do not send emails unless explicitly told to do so by the user. The user my explicitly say the word "send".
Always let the user review the email before sending it and ask for confirmation.
Never ever make up or invent email addresses if you don't actually know the email address.
"""

_starter_prompt = """You are a helpful assistant that helps people with their daily tasks.
Every single response to the user must use Markdown for formatting to make it neat and readable. Use tables for data. Add linebreaks where necessary for readability.
Do not duplicate data when formatting.
You can use multiple functions one after the other if you deem it necessary, before giving a final response.
However, if you need to call the same function on multiple different sets of arguments/information, use the run_on_list!
For example if the user requests certain information about a list, use run_on_list.
When using run_on_list, don't call the target function beforehand, run_on_list will do that for you.
Remember that some tasks can be completed using information you already have, without new function calls.
Only repeat actions if it is necessary.
In your responses only include information that is relevant to the user's query.
If presenting requested information, keep your own comments to a minimum.
If needed ask the user clarifying questions instead of immediately working on the task.
Use complete_task as much as possible for anything that is even slightly complex.
"""


class Conversator:
    """
    The conversator class. Processes a single message and returns a response.
    Processes all the function calls required.
    """

    functions: dict[str, GPTFunction]

    def __init__(self, functions: list):
        self.all_functions = functions
        openai.api_key = keys.openai_key
        self.internal_messages = [{"role": "system", "content": _starter_prompt}]
        self.last_internal_msg_len = 1
        self.functions = {}
        self.last_msg_len = 0
        for function in functions:
            self.functions[function.name] = function

        config = yaml.safe_load(open("config.yaml"))
        self.model_name = config["model"]["main"]

    def process_msg(self, msg: str) -> str:
        """
        Process a single message from the user.
        Either return a response or call a function until the LLM returns a response.
        :param msg: The message from the user
        :return: The final response to the user
        """
        st.session_state["messages"].append({"role": "user", "content": msg})
        self.internal_messages.append({"role": "user", "content": msg})
        available_data = {}
        for name, data in core.get_all_data_details().items():
            available_data[name] = data["summary"]
        available_data = json.dumps(available_data, indent=4)
        data_message = [{"role": "system", "content": f"Data available from storage:\n{available_data}"}]
        with st.spinner("Thinking..."):
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=self.internal_messages + data_message,
                functions=list(map(lambda x: x.to_dict(), self.functions.values())),
                function_call="auto"
            )
        message = response["choices"][0]["message"]

        while message.get("function_call"):
            func_name = message["function_call"]["name"]
            print(message["function_call"]["arguments"])
            func_args = json.loads(message["function_call"]["arguments"])
            if "reason" not in func_args:
                func_args["reason"] = "Working on it..."

            func = self.functions[func_name]
            if func.show_spinner:
                with st.spinner(f"{func_args['reason']}[{func_name}]"):
                    message = self.call_function(func, func_args)
            else:
                message = self.call_function(func, func_args)

        st.session_state["messages"].append(message)
        self.internal_messages.append(message)

        self.last_msg_len = len(st.session_state["messages"])
        self.last_internal_msg_len = len(self.internal_messages)
        return message["content"]

    def call_function(self, func: GPTFunction, args: dict):
        """
        Calls a function with the parameters given.
        Sends the result to the LLM and returns the response.
        :param func: the function to call
        :param args: the arguments of the function to call
        """
        func_result = func(args)
        self.internal_messages.append({"role": "function", "name": func.name, "content": func_result})
        message = openai.ChatCompletion.create(
            model=self.model_name,
            messages=self.internal_messages,
            # + [{"role": "system", "content": "Only proceed if this achieved the desired result and no another function need to be called"}],
            functions=list(map(lambda x: x.to_dict(), self.functions.values())),
            function_call="auto"
        )
        message = message["choices"][0]["message"]
        return message

    def reset_to_last(self):
        """
        Resets the messages to the last successfully processed message
        TODO: fix this
        """
        st.session_state["messages"] = st.session_state["messages"][:self.last_msg_len]
        self.internal_messages = self.internal_messages[:self.last_internal_msg_len]

    def reset(self):
        """
        Removes all the messages and resets the internal messages to the starter prompt
        """
        st.session_state["messages"] = []
        self.internal_messages = [{"role": "system", "content": _starter_prompt}]
