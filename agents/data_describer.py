import openai
import pandas as pd
import json

def describe_dataframe(name: str, data: pd.DataFrame):
    """
    Extracts the important information from an html page.
    :param text: the text to extract from
    """

    columns = list(data.columns)
    rows = len(data)
    sample = data.head(3).to_json()

    content = {
        "name": name,
        "columns": columns,
        "n_rows": rows,
        "sample": sample
    }
    content = json.dumps(content, indent=4)

    prompt = """Look at the summary of the dataframe. Generate a short description of the dataframe.
    It should describe the contents of the dataframe in a way that is easy to understand. One sentence maximum
    The description should be maximally succinct, don't say things like 'This dataframe contains'"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": content}
        ]
    )
    return response["choices"][0]["message"]["content"]