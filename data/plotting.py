from src.gpt_function import gpt_function
import data.core as core
import re
import os
from subprocess import Popen, PIPE
from time import sleep
from matplotlib import pyplot as plt
import streamlit as st
import traceback
import numpy as np


@gpt_function
def plot_data(plotting_code: str, data_name: str):
    """
    Useful for plotting and visualizing data.
    Before calling this function allways call 'get_data_details' to understand the structure of the data.
    :param plotting_code: the python code to be used to plot the data.
    Load the data from "temp/data.csv". There are no json files.
    Save the plot to a file called "temp/plot.png".1
    The plot MUST be saved to a file called "temp/plot.png" and the code MUST NOT output anything else.
    This should be the code and just the code, do not add any additional comments or text.
    Remember that this may not be straightforward so you may need to do data transformations using pandas.
    The data only has the columns listed.
    :param data_name: the name of the data to be plotted. This will be automatically written from memory to
    a file called "temp/data.csv". Your script can then access it.
    """

    print("Code:")
    print(plotting_code)

    plotting_code = re.sub(r"import.*\n", "", plotting_code)
    plotting_code = re.sub(r"= pd.read.*\n", "= pd.read_csv('temp/data.csv')", plotting_code)

    plotting_code = f"{data_name} = pd.read_csv('temp/data.csv')\n" + plotting_code
    plotting_code = "import pandas as pd\n" \
                    "import math\n" \
                    "import numpy as np\n" \
                    "import matplotlib.pyplot as plt\n" \
                    "import seaborn as sns\n" + plotting_code

    # Save the data to a csv file
    os.makedirs("temp", exist_ok=True)
    data = core.get_data(data_name)
    if data is None:
        return {"error": "The dataset does not exist. Please store the dataset first."}
    data.to_csv("temp/data.csv", index=False)

    with open("temp/plotting.py", "w") as f:
        f.write(plotting_code)
    try:
        process = Popen(["python", "temp/plotting.py"], stdout=PIPE, stderr=PIPE)
        while process.poll() is None:
            sleep(0.1)
        img = np.array(plt.imread("temp/plot.png"))
        st.image(img)
        st.session_state["messages"].append({"role": "image", "content": img})
        os.remove("temp/plot.png")
    except Exception as e:
        traceback.print_exc()
        return {"error": "The plotting code could not be executed. Please check your code and try again."}
    else:
        return {
            "result": "The plot has been displayed to the user. No additional output is required. Do not output the code"}
