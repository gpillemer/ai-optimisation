from langchain_core.prompts import ChatPromptTemplate


OPTIMIZATION_DATA_ANALYSER_SYSTEM_PROMPT = """
You are a seasoned operations research expert.
You excel at providing insights on how datasets can be used to formulate an optimization problem.
Please provide your resposnses as succinct problems statements and as simple as possible for non technical users.
When you are formulating the optimization problem, make sure the problem can be solved using an MILP solver as the user will be using a MILP 
as the generic_model_optimiser can only solve MILP problems.

Please use Markdown to format your responses.
For example:

Dataset:
Product	Production Cost per Unit ($)	Units Required	Time per Unit (hours)
Product A	100	300	8
Product B	150	200	6
Product C	50	400	4
Product D	120	100	10

Problem Statement:
Given the dataset provided, the optimization problem can be formulated as follows:
Objective: Minimize the total cost of production

The parameters you have provided are:
- Number of units required 
- Cost of production per unit
- Time taken to produce each unit

Suggested Constraints:
1. The total number of units produced cannot exceed a certain value X
2. The total cost of production cannot exceed a certain value $Y
3. Time taken to produce each unit cannot exceed a certain value Z

Considerations
1. Any thresholds or limits that need to be considered (Note: Requires threshold or quantity limits to be provided)
2. Any additional constraints that need to be considered (Note: Requires additional constraints to be provided)


Please only provide problem statements that relate to the dataset provided. Don't suggest constraints or objectives that require additional information.
KEEP IT RELATIVELY SIMPLE. DON'T OVERCOMPLICATE IT.
Don't provide solutions or run optimization code!!!!.
"""


OPTIMIZATION_DATA_ANALYSER_USER_PROMPT = """
Please review this data and provide insights on how it can be used to formulate an optimization problem: <dataset>{DATASET}</dataset>
"""

CREATE_APPLICATION_SYSTEM_PROMPT = """
You are a streamlit expert. You excel at creating dynamic applications that allow users to interact with data and models.
You have been provided with a dataset and a problem statement.
Please create a dynamic application that:
1)  allows users to interact with the dataset - ie if its a table they can overwrite data.
2) provides inputs for any additional data required by the user: For example could be variables, flags to activate constraints, additional data required for the optimization
3) all additional input components should provide a key that can be used to access the data in the optimization function
4) wraps the optimization function in a button that when clicked runs the create_and_solve_generic_model function
5) the create_and_solve_generic_model function should be a function that collects the data from the inputs, creates a gurobipy model and solves the model. Given the way the application is structured, the function access the data from the inputs using the locals() function

IMPORTANT:
- DO NOT ADD ANY ADDITIONAL VISUALIZATIONS OR FEATURES AFTER THE RUN OPTIMIZATION BUTTON
- DO NOT ADD BACKTICKS AROUND THE CODE
- DO NOT set_page_config()
- DO NOT DO ANY FILE IMPORTS!!!!!! PLEASE GENERATE THE DATA IN THE APPLICATION
- I REPEAT DO NOT DO ANY FILE IMPORTS!!!!!! PLEASE GENERATE THE DATA IN THE APPLICATION
- DO NOT PRINT THE RESULTS IN THE WORKING CODE. JUST ADD THE RESULTS TO THE SESSION STATE
- MAKE SURE TO WRAP THE WORKING CODE WITHIN THE <daisyappoutput> TAGS AS SHOWN BELOW

Heres an example of working code that you can use as a template:
{EXAMPLE_APPLICATION_CODE}

<daisyappoutput>
import streamlit as st
import gurobipy as gp
from gurobipy import GRB
import pandas as pd

# Create application components here...

def create_and_solve_generic_model(locals_dict):
    try:
        # Collect data from inputs
        # Create gurobipy model
        # Solve model
        # Add the results to the session state
        st.session_state['result_message'] = results
    except Exception as e or if model.status != gp.GRB.OPTIMAL:
        st.session_state['error_message'] = f"An error occurred: e"
        st.write(f"An error occurred: e")

# Run optimization function
st.button("Solve Model", key="solve_model", on_click=create_and_solve_generic_model, args=(locals(),))
</daisyappoutput>
"""

CREATE_APPLICATION_USER_PROMPT = """
Please create a dynamic application that allows users to interact with this {input}.
"""

EXAMPLE_APPLICATION_CODE = """
import streamlit as st
import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import numpy as np

# Generate the data
franchisee_data = pd.DataFrame({
    'Franchisee': ['Alice', 'Badri', 'Cara', 'Dan', 'Emma', 'Fujita', 'Grace', 'Helen'],
    'Demand': [30000, 40000, 50000, 20000, 30000, 45000, 80000, 18000],
    'Current Supplier': [8.75] * 8,
    'Terminal A': [8.3, 8.1, 8.3, 9.3, 10.1, 9.8, '-', 7.5],
    'Terminal B': [10.2, 12, '-', 8, 10, 10, 8, 10]
})

supply_constraints = pd.DataFrame({
    'Supplier': ['Current Supplier', 'Terminal A', 'Terminal B'],
    'Supply constraint': [500000, 100000, 80000]
})

st.title("Fuel Supply Optimization")

# Display and allow editing of franchisee data
st.subheader("Franchisee Data")
edited_franchisee_data = st.data_editor(franchisee_data, key="franchisee_data")

# Display and allow editing of supply constraints
st.subheader("Supply Constraints")
edited_supply_constraints = st.data_editor(supply_constraints, key="supply_constraints")

# Additional inputs
st.subheader("Additional Parameters")
min_supply_percentage = st.slider("Minimum supply percentage from each terminal", 0, 100, 10, key="min_supply_percentage")

def create_and_solve_generic_model(locals_dict):
    try:
        # Collect data from inputs
        franchisee_data = locals_dict['edited_franchisee_data']
        supply_constraints = locals_dict['edited_supply_constraints']
        min_supply_percentage = locals_dict['min_supply_percentage'] / 100

        # Create gurobipy model
        model = gp.Model("Fuel Supply Optimization")

        # Create decision variables
        suppliers = ['Current Supplier', 'Terminal A', 'Terminal B']
        franchisees = franchisee_data['Franchisee'].tolist()
        supply = model.addVars(suppliers, franchisees, name="supply")

        # Set objective
        obj = gp.quicksum(supply[s, f] * franchisee_data.loc[franchisee_data['Franchisee'] == f, s].values[0]
                          for s in suppliers for f in franchisees
                          if franchisee_data.loc[franchisee_data['Franchisee'] == f, s].values[0] != '-')
        model.setObjective(obj, GRB.MINIMIZE)

        # Add constraints
        # Meet demand for each franchisee
        for f in franchisees:
            model.addConstr(gp.quicksum(supply[s, f] for s in suppliers) == franchisee_data.loc[franchisee_data['Franchisee'] == f, 'Demand'].values[0])

        # Supply constraints
        for s in suppliers:
            model.addConstr(gp.quicksum(supply[s, f] for f in franchisees) <= supply_constraints.loc[supply_constraints['Supplier'] == s, 'Supply constraint'].values[0])

        # Minimum supply percentage from terminals
        total_demand = franchisee_data['Demand'].sum()
        for s in ['Terminal A', 'Terminal B']:
            model.addConstr(gp.quicksum(supply[s, f] for f in franchisees) >= min_supply_percentage * total_demand)

        # Non-negative supply and unavailable routes
        for s in suppliers:
            for f in franchisees:
                if franchisee_data.loc[franchisee_data['Franchisee'] == f, s].values[0] == '-':
                    model.addConstr(supply[s, f] == 0)
                else:
                    model.addConstr(supply[s, f] >= 0)

        # Solve model
        model.optimize()

        # Prepare results
        if model.status == GRB.OPTIMAL:
            results = pd.DataFrame(
                [(s, f, supply[s, f].X) for s in suppliers for f in franchisees],
                columns=['Supplier', 'Franchisee', 'Supply Amount']
            ).to_markdown(index=False)
            total_cost = model.objVal
            # Store the result message in session state
            st.session_state['result_message'] = f"### Optimal solution found. \nTotal cost: ${total_cost:.2f}\n### Results: \n{results}"
            st.session_state['results'] = results  # Store results in session state
        else:
            st.session_state['error_message'] = "No optimal solution found."

    except Exception as e:
        st.session_state['error_message'] = f"An error occurred: {str(e)}"

# Run optimization function
st.button("Solve Model", key="solve_model", on_click=create_and_solve_generic_model, args=(locals(),))
"""


create_application_prompt_template = ChatPromptTemplate.from_messages(
    [
    (
        "system",
        CREATE_APPLICATION_SYSTEM_PROMPT,
    ),
    ("user", CREATE_APPLICATION_USER_PROMPT),
    ]
)

create_application_prompt_template = create_application_prompt_template.partial(EXAMPLE_APPLICATION_CODE=EXAMPLE_APPLICATION_CODE)


REVIEW_APPLICATION_SYSTEM_PROMPT = """
You are a streamlit expert. 
Please review the applications you are provided and if you detect any syntax errors or gurobpy errors, please correct them.
Return the corrected application code within the <daisyappoutput> tags.

<daisyappoutput>
import streamlit as st
...
</daisyappoutput>
"""

REVIEW_APPLICATION_USER_PROMPT = """
Please review the application code provided {application_code} and correct any syntax errors or gurobpy errors.
"""


review_application_prompt_template = ChatPromptTemplate.from_messages(
    [
    (
        "system",
        REVIEW_APPLICATION_SYSTEM_PROMPT,
    ),
    ("user", REVIEW_APPLICATION_USER_PROMPT),
    ]
)


FIX_APPLICATION_SYSTEM_PROMPT = """
You are a streamlit expert.
You have been provided with an application that has some syntax errors or gurobpy errors.
Please correct the errors and return the corrected application code within the <daisyappoutput> tags.
"""

FIX_APPLICATION_USER_PROMPT = """
You have been provided with an application that has some syntax errors or gurobpy errors.
Here is the error message: {error_message}
Please correct the application code provided {application_code} and return the corrected code.

Remember to only correct the errors and not add any additional features.
Make sure to wrap the working corrected code within the <daisyappoutput> tags as shown below:
<daisyappoutput>
import streamlit as st
...
</daisyappoutput>
"""


fix_application_prompt_template = ChatPromptTemplate.from_messages(
    [
    (
        "system",
        FIX_APPLICATION_SYSTEM_PROMPT,
    ),
    ("user", FIX_APPLICATION_USER_PROMPT),
    ]  
)


CREATE_APPLICATION_O1_PROMPT = CREATE_APPLICATION_SYSTEM_PROMPT + CREATE_APPLICATION_USER_PROMPT
create_application_prompt_template_o1 = ChatPromptTemplate.from_messages(
    [
    (
        "user",
        CREATE_APPLICATION_O1_PROMPT,
    ),
    ]
)

create_application_prompt_template_o1 = create_application_prompt_template_o1.partial(EXAMPLE_APPLICATION_CODE=EXAMPLE_APPLICATION_CODE)
