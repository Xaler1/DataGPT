import streamlit as st
import pandas as pd
from collections import deque

def save_new_data(data: pd.DataFrame, name: str, summary: str):
    st.session_state["data"][name] = deque(maxlen=5)
    st.session_state["data"][name].append({"data": data, "summary": summary, "columns": list(data.columns)})

def update_data(data: pd.DataFrame, name: str):
    old_summary = st.session_state["data"][name][-1]["summary"]
    st.session_state["data"][name].append({"data": data, "summary": old_summary, "columns": list(data.columns)})

def undo_data(name: str) -> bool | None:
    if name not in st.session_state["data"]:
        return None
    if len(st.session_state["data"][name]) == 1:
        return False
    st.session_state["data"][name].pop()
    return True

def get_data(name: str) -> pd.DataFrame | None:
    if name not in st.session_state["data"]:
        return None
    return st.session_state["data"][name][-1]["data"]

def get_data_details(name: str) -> dict | None:
    if name not in st.session_state["data"]:
        return None
    return st.session_state["data"][name][-1]

def get_all_data_details() -> dict:
    all_data = {}
    for name in st.session_state["data"]:
        all_data[name] = st.session_state["data"][name][-1]
    return all_data