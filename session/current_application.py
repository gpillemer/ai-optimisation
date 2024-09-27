
import streamlit as st
import pandas as pd
import numpy as np

# Initialize the dataset
@st.cache_data
def load_data():
    data = {
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'Monday': ['9 AM - 5 PM', '10 AM - 4 PM', '9 AM - 5 PM', 'Off', '9 AM - 1 PM'],
        'Tuesday': ['10 AM - 6 PM', 'Off', '9 AM - 5 PM', '9 AM - 1 PM', '1 PM - 5 PM'],
        'Wednesday': ['9 AM - 5 PM', '10 AM - 4 PM', 'Off', '9 AM - 5 PM', '10 AM - 2 PM'],
        'Thursday': ['Off', '9 AM - 1 PM', '10 AM - 6 PM', 'Off', '9 AM - 5 PM'],
        'Friday': ['9 AM - 1 PM', '10 AM - 4 PM', '9 AM - 5 PM', 'Off', '1 PM - 5 PM'],
        'Number of shifts': [3, 2, 8, 10, 25]
    }
    return pd.DataFrame(data)

# Load the initial data
df = load_data()

st.title("Staff Scheduling Optimization")

# Display and edit the schedule
st.subheader("Current Schedule")
edited_df = st.data_editor(df, num_rows="dynamic")

# Additional parameters
st.subheader("Optimization Parameters")
min_staff = st.number_input("Minimum staff required at any time", min_value=1, value=2)
max_hours_per_week = st.number_input("Maximum hours per week per employee", min_value=0, value=40)
balance_weight = st.slider("Weight for balancing part-time and full-time (0-1)", 0.0, 1.0, 0.5)

# Constraints
st.subheader("Constraints")
enforce_max_shifts = st.checkbox("Enforce maximum number of shifts", value=True)
allow_overlapping_shifts = st.checkbox("Allow overlapping shifts", value=False)

# Additional employee information
st.subheader("Employee Information")
employee_types = {}
for name in edited_df['Name']:
    employee_type = st.selectbox(f"Employee type for {name}", ['Full-time', 'Part-time'])
    employee_types[name] = employee_type

# Run optimization button
if st.button("Run Optimization", key="run_optimization"):
    run_optimization()

# Display optimization results
if 'results' in globals():
    st.subheader("Optimization Results")
    st.table(results)
