import yaml
import openai
from secret import keys

_starter_prompt = """You are an intelligent agent that will be completing a task step by step.
First you must break down the task into smaller steps. Format them as a json list of steps.
E.g. {"steps" : ["Step 1: Do this", "Step 2: Do that", "Step 3: Do the other thing"]}
Take note of the functions available to you. Use to help complete the task, and take them into account when planning.
Do not break down the task into too many steps, as this will make it harder to complete.
Next you will be prompted step by step to complete the task. 
The user does not see this conversation, therefore you cannot ask them any questions.
You will need to verify that each step has been completed before moving on to the next one.
Do NOT provide any commentary at all whatsoever or information that is not relevant to the task.
"""

class BasicAgent:
    def __init__(self, functions):
        openai.api_key = keys.openai_key
        config = yaml.safe_load(open("config.yaml", "r"))
        self.model_name = config["model"]["agent"]
        self.messages = [{"role": "system", "content": _starter_prompt}]
        self.functions = {}
        for function in functions:
            self.functions[function.name] = function

    def run(self, task: str):
        self.messages.append({"role": "system", "content": f"The task is: {task}. Now produce a plan. The next message must be a single json plan"})
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=self.messages,
            functions=list(map(lambda x: x.to_dict(), self.functions.values())),
            function_call="auto"
        )
        self.messages.append(response["choices"][0]["message"])
        print(response["choices"][0]["message"]["content"])
        return response["choices"][0]["message"]["content"]
