
import streamlit as st
import pandas as pd
import gurobipy as gp

# Create the franchisee data
franchisee_data = {
    'Franchisee': ['Alice', 'Badri', 'Cara', 'Dan', 'Emma', 'Fujita', 'Grace', 'Helen'],
    'Demand': [30000, 40000, 50000, 20000, 30000, 45000, 80000, 18000],
    'Current Supplier': [8.75] * 8,
    'Terminal A': [8.3, 8.1, 8.3, 9.3, 10.1, 9.8, '-', 7.5],
    'Terminal B': [10.2, 12, '-', 8, 10, 10, 8, 10]
}

# Create the supply constraint data
supply_constraint_data = {
    'Supplier': ['Current Supplier', 'Terminal A', 'Terminal B'],
    'Supply constraint': [500000, 100000, 80000]
}

# Convert to DataFrames
df_franchisee = pd.DataFrame(franchisee_data)
df_supply = pd.DataFrame(supply_constraint_data)

# Display franchisee data
st.subheader("Franchisee Data")
edited_df_franchisee = st.data_editor(df_franchisee, num_rows="dynamic")

# Display supply constraint data
st.subheader("Supply Constraint Data")
edited_df_supply = st.data_editor(df_supply, num_rows="dynamic")

# Additional inputs
st.subheader("Additional Inputs")
min_supply_percentage = st.slider("Minimum supply percentage from current supplier", 0, 100, 0, key="min_supply_percentage")
max_terminals = st.number_input("Maximum number of terminals per franchisee", min_value=0, max_value=2, value=2, key="max_terminals")

# Open text field for additional constraints
additional_constraints = st.text_area("Additional constraints or data (free text)", key="additional_constraints")

def create_and_solve_generic_model(locals_dict):
    try:
        # Access the data from the inputs
        franchisee_df = locals_dict['edited_df_franchisee']
        supply_df = locals_dict['edited_df_supply']
        min_supply_percentage = locals_dict['min_supply_percentage']
        max_terminals = locals_dict['max_terminals']

        # Create the model
        model = gp.Model("Fuel Supply Optimization")

        # Create sets
        franchisees = franchisee_df['Franchisee'].tolist()
        suppliers = supply_df['Supplier'].tolist()

        # Create variables
        supply = model.addVars(franchisees, suppliers, vtype=gp.GRB.CONTINUOUS, name="supply")
        use_terminal = model.addVars(franchisees, suppliers[1:], vtype=gp.GRB.BINARY, name="use_terminal")

        # Set objective
        obj = gp.quicksum(supply[f, s] * franchisee_df.loc[franchisee_df['Franchisee'] == f, s].iloc[0] 
                          for f in franchisees for s in suppliers 
                          if franchisee_df.loc[franchisee_df['Franchisee'] == f, s].iloc[0] != '-')
        model.setObjective(obj, gp.GRB.MINIMIZE)

        # Add constraints
        # Meet demand
        for f in franchisees:
            model.addConstr(gp.quicksum(supply[f, s] for s in suppliers) == franchisee_df.loc[franchisee_df['Franchisee'] == f, 'Demand'].iloc[0])

        # Supply constraints
        for s in suppliers:
            model.addConstr(gp.quicksum(supply[f, s] for f in franchisees) <= supply_df.loc[supply_df['Supplier'] == s, 'Supply constraint'].iloc[0])

        # Minimum supply from current supplier
        for f in franchisees:
            model.addConstr(supply[f, 'Current Supplier'] >= min_supply_percentage/100 * franchisee_df.loc[franchisee_df['Franchisee'] == f, 'Demand'].iloc[0])

        # Maximum number of terminals
        for f in franchisees:
            model.addConstr(gp.quicksum(use_terminal[f, s] for s in suppliers[1:]) <= max_terminals)

        # Link supply to use_terminal
        for f in franchisees:
            for s in suppliers[1:]:
                if franchisee_df.loc[franchisee_df['Franchisee'] == f, s].iloc[0] != '-':
                    model.addConstr(supply[f, s] <= franchisee_df.loc[franchisee_df['Franchisee'] == f, 'Demand'].iloc[0] * use_terminal[f, s])
                else:
                    model.addConstr(supply[f, s] == 0)

        # Solve the model
        model.optimize()

        # Prepare results
        if model.status == gp.GRB.OPTIMAL:
            results = "Optimal solution found:\n\n"
            for f in franchisees:
                results += f"Franchisee {f}:\n"
                for s in suppliers:
                    if supply[f, s].x > 0:
                        results += f"  - Supplied {supply[f, s].x:.2f} from {s}\n"
            results += f"\nTotal Cost: {model.objVal:.2f}"
        else:
            results = "No optimal solution found."

        st.session_state['result_message'] = results

    except Exception as e:
        st.session_state['result_message'] = f"An error occurred: {str(e)}"

# Run optimization function
st.button("Solve Model", key="solve_model", on_click=create_and_solve_generic_model, args=(locals(),))
