import json
import inspect
import docstring_parser as docparser
import streamlit as st
import traceback


class GPTFunction:
    """
    A wrapper for other functions to become GPT functions,
    which can be passed to an LLM for use.
    """

    def __init__(self,
                 name: str,
                 description: str,
                 properties: dict,
                 required: list = None,
                 func_callable: callable = None,
                 show_spinner: bool = True
                 ):

        if required is None:
            required = []
        self.name = name
        self.description = description
        self.properties = properties
        self.required = required
        self.func_callable = func_callable
        self.show_spinner = show_spinner

        self.properties["reason"] = {
            "type": "string",
            "description": "What are you doing by using this function. In present tense with '-ing' ending. Always required."
        }
        self.required.append("reason")

    def to_dict(self) -> dict:
        """
        Convert the function to a dictionary in the OpenAI function format
        :return: the function as a dictionary
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": self.properties,
                "required": self.required
            }
        }

    def __call__(self, args: dict) -> str:
        """
        Calls the inner function with the given parameters
        The parameters are converted to the correct types
        :param args: the parameters to pass to the function
        :return: the output of the function as a JSON string
        """

        args.pop("reason")
        # Covert to correct types
        for property in self.properties:
            if property in args:
                if self.properties[property]["type"] == "integer":
                    args[property] = int(args[property])
                elif self.properties[property]["type"] == "array":
                    args[property] = args[property]
                    if self.properties[property]["items"]["type"] == "integer":
                        args[property] = list(map(int, args[property]))
                    elif self.properties[property]["items"]["type"] == "number":
                        args[property] = list(map(float, args[property]))
                elif self.properties[property]["type"] == "number":
                    args[property] = float(args[property])

        result = self.func_callable(**args)
        return json.dumps(result, indent=4)


def gpt_function(func) -> GPTFunction:
    """
    A decorator to convert a function to a GPT function
    Parses the description and parameters from the docstring as well as their types
    from the signature.
    :param func: the function to convert
    :return: the wrapped GPT function
    """
    mapping = {
        "str": "string",
        "int": "integer",
        "float": "number",
        "list": "array",
    }

    try:
        docstring = docparser.parse(func.__doc__)
        signature = inspect.signature(func)
        parameters = signature.parameters

        # Check that the docstring has the same number of parameters as the function
        if len(docstring.params) != len(parameters):
            st.error(f"""
            The number of parameters in the docstring of the '{func.__name__}' function
            does not match the number of parameters in the function itself.
            """)
            st.stop()
            return None

        # Check that the docstring has the same parameters as the function
        for index, param in enumerate(parameters):
            if docstring.params[index].arg_name != param:
                st.error(f"""
                The parameter '{docstring.params[index].arg_name}' in the docstring of the
                '{func.__name__}' function does not match the parameter '{param}' in the
                function itself.
                """)
                st.stop()
                return None

        # Check that the docstring has a description for each parameter
        for index, param in enumerate(parameters):
            if docstring.params[index].description is None:
                st.error(f"""
                The parameter '{param}' in the docstring of the '{func.__name__}' function
                does not have a description.
                """)
                st.stop()
                return None

        # Check that the docstring has a description.
        description = docstring.long_description
        if description is None:
            description = docstring.short_description
        if description is None or description == "":
            st.error(f"""
            The docstring of the '{func.__name__}' function does not have a description.
            """)
            st.stop()
            return None

        properties = {}
        required = []
        for index, param in enumerate(parameters):
            param_type = mapping.get(parameters[param].annotation.__name__, "string")
            properties[param] = {
                "type": param_type,
                "description": docstring.params[index].description.replace("\n", " ")
            }
            # Extract the inner type of the array
            if param_type == "array":
                properties[param]["items"] = {
                    "type": mapping.get(parameters[param].annotation.__args__[0].__name__, "string")
                }
            if parameters[param].default is inspect.Parameter.empty:
                required.append(param)

    except Exception:
        st.error(f"Error parsing the '{func.__name__}' function")
        st.code(traceback.format_exc())
        st.stop()
        return None

    return GPTFunction(
        name=func.__name__,
        description=description,
        properties=properties,
        required=required,
        func_callable=func,
    )


def gpt_agent(func) -> GPTFunction:
    function = gpt_function(func)
    function.show_spinner = False
    return function
