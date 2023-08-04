import streamlit as st
import pandas as pd
from collections import deque


def save_new_data(data: pd.DataFrame, name: str, summary: str):
    """
    Creates a new memory queue in the session state and saves the data to it.
    :param data: the data in a dataframe to save
    :param name: the name of the data
    :param summary: the summary of the data
    """
    st.session_state["data"][name] = deque(maxlen=5)
    st.session_state["data"][name].append({"data": data, "summary": summary, "columns": list(data.columns)})


def update_data(data: pd.DataFrame, name: str):
    """
    Adds a new version of the data to the queue in the session state.
    :param data: the data in a dataframe
    :param name: the name of the data
    """
    old_summary = st.session_state["data"][name][-1]["summary"]
    st.session_state["data"][name].append({"data": data, "summary": old_summary, "columns": list(data.columns)})


def undo_data(name: str) -> bool | None:
    """
    Removes the last version of the data from the queue in the session state.
    Only does so if there is more than one version of the data.
    :param name: the name of the data
    :return: True if the data was removed, False if there was only one version of the data, None if the data does not exist
    """
    if name not in st.session_state["data"]:
        return None
    if len(st.session_state["data"][name]) == 1:
        return False
    st.session_state["data"][name].pop()
    return True


def get_data(name: str) -> pd.DataFrame | None:
    """
    Get the latest version of the data from the queue in the session state.
    :param name: the name of the data
    :return: the latest version of the data, or None if the data does not exist
    """
    if name not in st.session_state["data"]:
        return None
    return st.session_state["data"][name][-1]["data"]


def get_data_details(name: str) -> dict | None:
    """
    Get the details of the latest version of the data from the queue in the session state.
    :param name: the name of the data
    :return: the details of the latest version of the data, or None if the data does not exist
    """
    if name not in st.session_state["data"]:
        return None
    return st.session_state["data"][name][-1]


def get_all_data_details() -> dict:
    """
    Get the details of all the data from the queue in the session state.
    :return: the details of all the data
    """
    all_data = {}
    for name in st.session_state["data"]:
        all_data[name] = st.session_state["data"][name][-1]
    return all_data
