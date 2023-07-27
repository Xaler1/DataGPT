from src.gpt_function import gpt_function
import streamlit as st
import re
import os
from subprocess import Popen, PIPE
from time import sleep

@gpt_function
def plot_data(plotting_code: str, data_name: str):
    """
    Useful for plotting and visualizing data.
    Before calling this function allways call 'get_data_details' to understand the structure of the data.
    :param plotting_code: write a python function called "plotting" to plot the data. The function should accept a
    variable called "data" which will contain the desired data to be plotted. The function should return the complete figure.
    Provide all of the code of this function starting with the "def" and ending with the return statement.
    Use figure = plt.figure() to create the figure at the very start and then return that figure.
    :param data_name: the name of the data to be plotted.
    """

    print("Code:")
    print(plotting_code)

    # Check if the data exists
    if data_name not in st.session_state["data"]:
        return {"error": "The dataset does not exist. Please store the dataset first."}

    # Remove all import lines and lines that attempt to read a file
    plotting_code = re.sub(r"import.*\n", "", plotting_code)
    plotting_code = re.sub(r"pd.read_csv.*\n", "", plotting_code)

    # Save the data to a csv file
    os.makedirs("temp", exist_ok=True)
    data = st.session_state["data"][data_name]["data"]
    data.to_csv("temp/data.csv", index=False)

    plotting_code = "import pandas as pd\nimport math\nimport numpy as np\nimport matplotlib.pyplot as plt\n" + plotting_code

    with open("temp/plotting.py", "w") as f:
        f.write(plotting_code)

    try:
        from temp.plotting import plotting
        fig = plotting(data)
        fig.savefig("temp/plot.png")
        st.pyplot(fig)
        st.session_state["messages"].append({"role": "plot", "content": fig})
    except Exception as e:
        return {"error": "The plotting code could not be executed. Please check your code and try again."}
    else:
        return {"result": "The plot has been displayed to the user. No additional output is required."}
