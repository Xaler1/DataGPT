from src.gpt_function import gpt_function
import os
from subprocess import Popen, PIPE
import data.core as core
import pandas as pd
import json
import re
from time import sleep


@gpt_function
def analyze_data(analysis_code: str, data_name: str):
    """
    Useful for analyzing data, extracting statistics. Answering questions about the data. The data is a pandas dataframe.
    Before calling this function ALWAYS call 'get_data_details' to understand the structure of the data.
    DO NOT use this for changing or transforming the data. Use 'transform_data' for that.
    :param analysis_code: the python code to be used to analyze the data. Load the data from a csv file.
    Put all of the results you need in a json called "result". There must be a single varible called "result"
    and it must be a dictionary of all the results you need.
    This should be the code and just the code, do not add any additional comments or text.
    Make sure to only use columns that are specified in the data. Remember, they can be slightly different from the user input!
    Think about what columns are needed and not what exactly the user inputted.
    :param data_name: the name of the data to be analyzed.
    """

    # Remove all import lines and lines that attempt to read a file
    analysis_code = re.sub(r"import.*\n", "", analysis_code)
    analysis_code = re.sub(r"= pd.read.*\n", "= pd.read_csv('temp/data.csv')", analysis_code)

    # Save the data to a csv file
    os.makedirs("temp", exist_ok=True)
    data = core.get_data(data_name)
    if data is None:
        return {"error": "The dataset does not exist. Please store the dataset first."}
    data.to_csv("temp/data.csv", index=False)

    # Load the data
    analysis_code = f"{data_name} = pd.read_csv('temp/data.csv')\n" + analysis_code
    analysis_code = "df = pd.read_csv('temp/data.csv')\n" + analysis_code
    analysis_code = "data = pd.read_csv('temp/data.csv')\n" + analysis_code
    # Add imports to the code
    analysis_code = "import pandas as pd\nimport math\nimport numpy as np\n" + analysis_code
    # Add the results print
    analysis_code += "\nprint(result)"

    with open("temp/analysis.py", "w") as f:
        f.write(analysis_code)
    process = Popen(["python", "temp/analysis.py"], stdout=PIPE, stderr=PIPE)
    while process.poll() is None:
        sleep(0.1)
    stdout, stderr = process.communicate()
    if stderr:
        return {"error": stderr.decode("utf-8")}
    else:
        print("\nResults:")
        result = stdout.decode("utf-8").replace("'", '"')
        print(result)
        try:
            results = json.loads(result)
        except Exception:
            results = result
        return {"results": results}


@gpt_function
def transform_data(transformation_code: str, data_name: str):
    """
    Useful for transforming data, e.g. sorting, pruning, dropping. The data is a pandas dataframe.
    Before calling this function ALWAYS call 'get_data_details' to understand the structure of the data.
    :param transformation_code: the python code to be used to transform the data.
    Load the data from "temp/data.csv". There are no json files.
    Save the transformed dataframe to "temp/data.csv". Remember to save the data!
    This should be the code and just the code, do not add any additional comments or text.
    Make sure to only use columns that are specified in the data. Remember, they can be slightly different from the user input!
    Think about what columns are needed and not what exactly the user inputted.
    :param data_name: the name of the data to be analyzed.
    """

    transformation_code = re.sub(r"import.*\n", "", transformation_code)
    transformation_code = re.sub(r"= pd.read_csv.*\n", "= pd.read_csv('temp/data.csv')", transformation_code)
    transformation_code = re.sub(r"to_csv.*\n", "to_csv('temp/data.csv', index=False)", transformation_code)

    transformation_code = f"{data_name} = pd.read_csv('temp/data.csv')\n" + transformation_code
    transformation_code = f"df = pd.read_csv('temp/data.csv')\n" + transformation_code
    transformation_code = f"data = pd.read_csv('temp/data.csv')\n" + transformation_code
    # Add imports to the code
    transformation_code = "import pandas as pd\nimport math\nimport numpy as np\n" + transformation_code

    # Find the last name to be assigned to checking which one appears last
    final_data_name = ""
    for idx, line in enumerate(transformation_code.split("\n")):
        if "=" in line:
            final_data_name = line[:line.index("=")].strip()
        if "to_csv" in line:
            final_data_name = line[:line.index(".")].strip()
    transformation_code += f"\n{final_data_name}.to_csv('temp/data.csv', index=False)"


    os.makedirs("temp", exist_ok=True)
    data = core.get_data(data_name)
    if data is None:
        return {"error": "The dataset does not exist. Please store the dataset first."}
    data.to_csv("temp/data.csv", index=False)

    with open("temp/transformation.py", "w") as f:
        f.write(transformation_code)
    process = Popen(["python", "temp/transformation.py"], stdout=PIPE, stderr=PIPE)
    while process.poll() is None:
        sleep(0.1)
    stdout, stderr = process.communicate()
    if stderr:
        return {"error": stderr.decode("utf-8")}
    transformed_data = pd.read_csv("temp/data.csv")
    core.update_data(transformed_data, data_name)
    return {"results": f"Data transformed successfully. There are now {len(transformed_data)} rows."}

@gpt_function
def undo_transformation(data_name: str):
    """
    Undoes the last transformation. This is useful if you want to undo a transformation.
    :param data_name: the name of the data to be undone.
    """
    result = core.undo_data(data_name)
    if result is None:
        return {"error": "This data name does not exist. Please check the data name."}
    if not result:
        return {"error": "There are no more transformations to undo."}
    new_data = core.get_data(data_name)
    return {"results": f"Transformation undone successfully. There are now {len(new_data)} rows."}
