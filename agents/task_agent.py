import yaml
import openai
import json
from secret import keys
from src.gpt_function import GPTFunction
from functions.gmaps import get_travel_distance
from agents.basic import run_on_list
from data.manipulation import analyze_data, transform_data, undo_transformation
from data.storage import get_data_details

_starter_prompt = """You are an intelligent agent that will be completing a task step by step.
First you must break down the task into smaller steps. Format them as a json list of steps.
E.g. {"steps" : ["Step 1: Do this", "Step 2: Do that", "Step 3: Do the other thing"]}
Take note of the functions available to you. Use to help complete the task, and take them into account when planning.
Do not break down the task into too many steps, as this will make it harder to complete.
The user does not see this conversation, therefore you cannot ask them any questions.
Do NOT provide any commentary at all whatsoever or information that is not relevant to the task.
Make sure that the output includes all of the information relevant to the task.
Your next response must be a single json plan.
Do not call functions unless it is actually necessary.
"""


class TaskAgent:
    def __init__(self, functions: list[GPTFunction]):
        openai.api_key = keys.openai_key
        config = yaml.safe_load(open("config.yaml", "r"))
        self.model_name = config["model"]["agent"]
        self.messages = []
        self.functions = {}
        for function in functions:
            self.functions[function.name] = function

    def get_response(self, prompt: str, allow_function_calls: bool = True):
        print("\nSystem:")
        print(prompt)
        self.messages.append({"role": "system", "content": prompt})
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=self.messages,
            functions=list(map(lambda x: x.to_dict(), self.functions.values())),
            function_call="auto" if allow_function_calls else "none"
        )["choices"][0]["message"]
        self.messages.append(response)

        if response.get("function_call") and allow_function_calls:
            func_name = response["function_call"]["name"]
            func_args = response["function_call"]["arguments"]
            func_args = json.loads(func_args)
            self.call_function(func_name, func_args)
            return None
        else:
            print("\nAgent:")
            print(response["content"])

        return response["content"]

    def call_function(self, func_name: str, func_args: dict):
        print("\nFunction call:\n", func_name, "\n", func_args)
        func = self.functions[func_name]
        func_results = func(func_args)
        print("\nFunction results:\n", func_results)
        self.messages.append({"role": "function", "name": func_name, "content": func_results})

    def run(self, task: str):
        prompt = f"""The task is: {task}"""
        prompt = _starter_prompt + prompt
        response = self.get_response(prompt, allow_function_calls=False)

        valid_plan = False
        while not valid_plan:
            try:
                steps = json.loads(response)["steps"]
                valid_plan = True
            except:
                prompt = f"The json you provided is not valid. Please try again. The next message must be a single json plan, do not apologize"
                response = self.get_response(prompt, allow_function_calls=False)

        for i in range(len(steps)):
            step = steps[i]
            completed = False
            step_prompt = f"""Okay, lets go onto the next step: {step}. Do whatever is necessary to complete it and output the result.
            Think about whether you need to call any functions, or do you already have all of the information needed?
            In a lot of cases you already know everything you need to know and can simply answer the question."""
            while not completed:
                self.get_response(step_prompt)
                prompt = f"""Has this achived the goal of step {step}? If so, respond with 'yes'. If not, respond with 'no'.
                Do no include anything else in the response. Just a "yes" or "no", do not repeat the plan"""
                response = self.get_response(prompt)
                if "yes" in response.lower():
                    completed = True
                else:
                    step_prompt = f"Please try again to complete step {step}. Fix whatever mistake was made. Remember, the user cannot help you"
            prompt = f"""The current plan is {steps}. Based on all of the above, does it need to be amended? If so, respond with 'yes'. If not, respond with 'no'
            Do not include anything else in the response. Just a "yes" or "no", do not repeat the plan"""
            response = self.get_response(prompt, allow_function_calls=False)
            if "yes" in response.lower():
                prompt = f"Please amend the plan to include the new step. The next message must be a single json plan"
                response = self.get_response(prompt)
                steps = json.loads(response)["steps"]

        prompt = f"The plan has been completed. Based on everything done above, what is the final output for the task of {task}?"
        response = self.get_response(prompt)
        return response


if __name__ == '__main__':
    functions = [
        get_travel_distance,
        analyze_data, transform_data, undo_transformation, get_data_details,
        run_on_list
    ]
    agent = TaskAgent(functions)
    agent.run("Calculate how long it would take to travel from London to Madrid. While stopping in Paris.")
