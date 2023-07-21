import json
import inspect
import docstring_parser as docparser
import streamlit as st
import traceback

class GPTFunction:
    def __init__(self,
                 name: str,
                 description: str,
                 properties: dict,
                 required: list = None,
                 func_callable: callable = None
                 ):

        if required is None:
            required = []
        self.name = name
        self.description = description
        self.properties = properties
        self.required = required
        self.func_callable = func_callable

        self.properties["reason"] = {
            "type": "string",
            "description": "What you think this function will do. In present tense with '-ing'"
        }
        self.required.append("reason")

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": self.properties,
                "required": self.required
            }
        }

    def __call__(self, args: dict):
        args.pop("reason")
        result = self.func_callable(**args)
        return json.dumps(result, indent=4)


def gpt_function(func):
    mapping = {
        "str": "string",
        "int": "integer",
        "list": "list"
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
        if docstring.short_description is None or docstring.short_description.strip() == "":
            st.error(f"""
            The docstring of the '{func.__name__}' function does not have a description.
            """)
            st.stop()
            return None

        properties = {}
        required = []
        for index, param in enumerate(parameters):
            properties[param] = {
                "type": mapping.get(str(parameters[param].annotation), "string"),
                "description": docstring.params[index].description
            }
            if parameters[param].default is inspect.Parameter.empty:
                required.append(param)
    except Exception as e:
        st.error(f"Error parsing the '{func.__name__}' function")
        st.code(traceback.format_exc())
        st.stop()
        return None

    return GPTFunction(
        name=func.__name__,
        description=docstring.short_description,
        properties=properties,
        required=required,
        func_callable=func
    )
