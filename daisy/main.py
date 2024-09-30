import sys
import streamlit as st
import pandas as pd
import numpy as np
from anthropic import Anthropic
from bs4 import BeautifulSoup
import os
import json
import yaml
import gurobipy as gp
from gurobipy import GRB
from chain import get_application_create_chain, get_application_fix

from prompts import OPTIMIZATION_DATA_ANALYSER_SYSTEM_PROMPT, OPTIMIZATION_DATA_ANALYSER_USER_PROMPT, CREATE_APPLICATION_SYSTEM_PROMPT, CREATE_APPLICATION_USER_PROMPT

default_configs = {
    "review_application_code": False,
    "use_o1": False
}

if len(sys.argv) > 1:
    CONFIGS = sys.argv[1]
    configs = json.loads(CONFIGS)
    configs = {k: v for k, v in configs.items() if k in default_configs}
else:
    configs = default_configs


review_application_code = configs.get("review_application_code", False)
use_o1 = configs.get("use_o1", False)

# Initialize session state variables if they don't exist
def initialize_session_state():
    st.session_state.setdefault("application_code", "")
    st.session_state.setdefault("dfs_string", "")
    st.session_state.setdefault("problem_statement", "")
    st.session_state.setdefault("uploaded_files", None)
    st.session_state.setdefault("result_message", "")
    st.session_state.setdefault("results_placeholder", None)

initialize_session_state()

# Initialize Anthropic client
client = Anthropic()


# Helper function to collect optimization data

def clear_session():
    session_dir = os.path.join("session")
    for file in os.listdir(session_dir):
        if file.startswith("data-"):
            os.remove(os.path.join(session_dir, file))

def collect_optimization_data(state):
    data = {}
    for k, v in state.items():
        if k not in ["application_code", "result_message","results_placeholder", "uploaded_files", "run_optimization", "load_application"] and not k.startswith("_"):
            data[k] = str(state[k])
    with open(os.path.join("session","optimization_data.json"), "w") as f:
        json.dump(data, f)
    return yaml.dump(data)


# Load application code from file
def load_application():
    with open(os.path.join("daisy","session","current_application.py"), "r") as f:
        st.session_state.application_code = f.read()

def fix_application_error_and_reload():
    application_error = st.session_state.error_message
    current_application = st.session_state.application_code
    new_application = get_application_fix(application_error, current_application)
    with open(os.path.join("daisy","session","current_application.py"), "w") as f:
        f.write(new_application)
        st.session_state.application_code = new_application
        st.session_state.error_message = None


# Extract output content from Anthropic response
def get_output(input_string):
    soup = BeautifulSoup(input_string, 'html.parser')
    return soup.find('output').text

# Generate optimization data analysis using Anthropic API
def generate_optimization_data_analysis(dataset, message_placeholder):
    st.session_state.problem_statement = ""
    message_placeholder.empty()

    with client.messages.stream(
        max_tokens=1024,
        system=OPTIMIZATION_DATA_ANALYSER_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": OPTIMIZATION_DATA_ANALYSER_USER_PROMPT.format(DATASET=dataset)}],
        model="claude-3-5-sonnet-20240620"
    ) as stream:
        for text in stream.text_stream:
            st.session_state.problem_statement += text
            message_placeholder.markdown(st.session_state.problem_statement)


def create_application(example_data, problem_statement):
    input_data = f"{example_data}\n{problem_statement}"
    create_application_chain = get_application_create_chain(review_application_code=review_application_code, use_o1=use_o1)
    application_code = create_application_chain.invoke(input_data)
    st.session_state.application_code = application_code
    
    with open(os.path.join("daisy","session","current_application.py"), "w") as f:
        f.write(st.session_state.application_code)

# Page 1: Application Generator
def page_one():
    st.title("Application Generator")

    # File uploader for CSV files
    uploaded_files = st.file_uploader("Choose a CSV file", type="csv", accept_multiple_files=True)
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files

    # Process uploaded files and generate problem statement
    if st.session_state.uploaded_files and not st.session_state.problem_statement:
        dfs = [pd.read_csv(file) for file in st.session_state.uploaded_files]
        st.session_state.dfs_string = "\n".join([df.to_string() for df in dfs])

        # Display data preview
        st.write("Here are the first 5 rows of your files:")
        for df in dfs:
            st.dataframe(df.head())

        analysis_message_placeholder = st.empty()

        # Generate problem statement using the Anthropic API
        with st.chat_message("user"):
            generate_optimization_data_analysis(st.session_state.dfs_string, message_placeholder=analysis_message_placeholder)

        # Button to generate application after problem statement is ready
        if st.session_state.problem_statement and not st.session_state.application_code:
            st.button("Generate Application", key="generate_application", on_click=create_application,
                      args=(st.session_state.dfs_string, st.session_state.problem_statement))

    elif st.session_state.problem_statement:
        st.write(st.session_state.problem_statement)
        st.button("Generate Application", key="generate_application", on_click=create_application,
                  args=(st.session_state.dfs_string, st.session_state.problem_statement))
    else:
        st.write("Please upload a CSV file.")

# Page 2: Display current application
def page_two():
    st.button("Load Application", key="load_application", on_click=load_application)

    if not st.session_state.application_code:
        st.write("Please generate an application first.")
    else:
        try:
            exec(st.session_state.application_code,{"st":st, "gp":gp,"GRB":GRB,"pd":pd},locals())
            if not st.session_state.results_placeholder:
                st.session_state.results_placeholder = st.empty()
            if st.session_state.result_message:
                st.session_state.results_placeholder.markdown(st.session_state.result_message)  
            
            if st.session_state.get("error_message"):
                st.button("Fix Error and Reload Application", key="fix_error", on_click=fix_application_error_and_reload)
                st.write(st.session_state.error_message)
                
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Sidebar navigation
st.sidebar.title("DAISY Decision AI System")
page = st.sidebar.radio("Go to", ["Application Generator", "Current Application"])

# Page routing
if page == "Application Generator":
    page_one()
else:
    page_two()
