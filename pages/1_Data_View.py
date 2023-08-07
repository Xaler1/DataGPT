import streamlit as st
import data.core as core
import pandas as pd
from agents.basic import describe_dataframe

st.set_page_config(
    page_title="Data View",
    page_icon="📊",
    layout="wide",
)

# Allow selection of data to show
st.title("View data")
st.text("Select the data you want to view")
idx = 0
if st.session_state["data_view"]["name"] is not None:
    idx = list(core.get_all_data_details().keys()).index(st.session_state["data_view"]["name"])
data_name = st.selectbox("data to view",
                         core.get_all_data_details().keys(),
                         index=idx,
                         label_visibility="collapsed",
                         placeholder="Select...")

# Allow uploading of new data
st.header("Upload more data")
uploaded_file = st.file_uploader("Upload data",
                                 type=["csv", "xlsx"],
                                 accept_multiple_files=False,
                                 key="data_upload",
                                 label_visibility="collapsed")
if uploaded_file is not None:
    dataframe = pd.read_csv(uploaded_file)
    name = uploaded_file.name.replace(".csv", "")
    if name not in st.session_state["data"]:
        with st.spinner("Processing..."):
            summary = describe_dataframe(name, dataframe)
        core.save_new_data(dataframe, name, summary)
        st.experimental_rerun()

if data_name is not None:
    st.session_state["data_view"]["name"] = data_name
    details = core.get_data_details(data_name)
    st.header("Summary")
    st.write(details["summary"])
    st.header("Columns to show")
    # If the columns haven't been set yet, set them to the be all columns
    if st.session_state["data_view"]["columns"] is None:
        st.session_state["data_view"]["columns"] = details["columns"]
    selected_columns = st.multiselect("columns to show",
                                      details["columns"],
                                      default=st.session_state["data_view"]["columns"],
                                      label_visibility="collapsed")
    st.session_state["data_view"]["columns"] = selected_columns

    st.header("Data")
    pruned_data = details["data"][selected_columns]
    st.dataframe(pruned_data)
    st.header("Download")
    st.download_button("Download current selection", pruned_data.to_csv().encode("utf-8"), "data.csv", "text/csv")