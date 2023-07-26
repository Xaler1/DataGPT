from matplotlib import pyplot as plt
from src.gpt_function import gpt_function
import streamlit as st

@gpt_function
def plot_data(x: list[float], y: list[float], title: str, xlabel: str, ylabel: str):
    """
    Useful for plotting data

    :param x: the list of x values
    :param y: the list of y values
    :param title: the title of the plot
    :param xlabel: the label for the x axis
    :param ylabel: the label for the y axis
    """

    params = {
        'axes.labelsize': 6,
        'axes.titlesize': 6,
        'xtick.labelsize': 6,
        'ytick.labelsize': 6,
        'axes.titlepad': 1,
        'axes.labelpad': 1,
        'font.size': 12
    }

    figure = plt.figure(figsize=(3, 2), dpi=100)
    plt.rcParams.update(params)
    plt.plot(x, y)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    st.session_state["messages"].append({"role": "plot", "content": figure})
    with st.container():
        st.pyplot(figure, use_container_width=False)
    return {"results": "The data has been plotted and already shown to the user. No additional output is required."}
