from src.gpt_function import gpt_function
import os
from subprocess import Popen, PIPE
import streamlit as st
import json
import re
from time import sleep

@gpt_function
def analyze_data(analysis_code: str, data_name: str):
    """
    Useful for analyzing data, extracting statistics. Answering questions about the data. The data is a pandas dataframe.
    Before calling this function allways call 'get_data_details' to understand the structure of the data.
    :param analysis_code: the python code to be used to analyze the data. The data will be stored in a variable called
    "data". Put all of the results you need in a json called "result". There must be a single varible called "result"
    and it must be a dictionary of all the results you need.
    This should be the code and just the code, do not add any additional comments or text.
    :param data_name: the name of the data to be analyzed.
    """

    # Check if the data exists
    if data_name not in st.session_state["data"]:
        return {"error": "The dataset does not exist. Please store the dataset first."}

    # Remove all import lines and lines that attempt to read a file
    analysis_code = re.sub(r"import.*\n", "", analysis_code)
    analysis_code = re.sub(r"data = pd.read_csv.*\n", "", analysis_code)
    analysis_code = re.sub(r"data = pd.read_excel.*\n", "", analysis_code)


    # Save the data to a csv file
    os.makedirs("temp", exist_ok=True)
    data = st.session_state["data"][data_name]["data"]
    data.to_csv("temp/data.csv", index=False)

    # Load the data
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