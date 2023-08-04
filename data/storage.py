from src.gpt_function import gpt_function
import pandas as pd
import json
import data.core as core


@gpt_function
def manual_write_data(data: str, name: str, summary: str):
    """
    Useful for storing data for future use.

    :param data: data in json format. This must be a single json in a format parseable into a pandas dataframe. Reformat the data if necessary
    :param name: the name of the data.
    :param summary: a short summary of what this data is.
    """
    data = json.loads(data)
    try:
        data = pd.DataFrame(data)
    except Exception:
        return {"error": "The data could not be parsed into a pandas dataframe. You must reformat the data and try again."}
    print("\nStoring data...")
    print(data)
    core.save_new_data(data, name, summary)

    return {"result": "The data has been stored. No additional output is required."}

@gpt_function
def get_data_details(name: str):
    """
    Useful for getting the details of data. The name, summary, columns, and sample of the dataframe will be returned.

    :param name: the name of the dataset.
    """

    data = core.get_data_details(name)
    if data == None:
        return {"error": "The dataset does not exist. Please store the dataset first."}
    else:
        summary = data["summary"]
        columns = data["columns"]
        sample = data["data"].head(1).to_json()
        return {
            "name": name,
            "summary": summary,
            "columns": columns,
            "sample": sample
        }


@gpt_function
def read_data(name: str):
    """
    Useful for reading all of the data. Do not use for analysis, use 'analyze_data' instead.
    Returns ALL of the data in the dataframe. which most likely will be overwhelming.

    :param name: the name of the dataframe.
    """
    data = core.get_data(name)
    if data is None:
        return {"error": "The dataset does not exist. Please store the dataset first."}
    else:
        return {"data": data.to_json()}