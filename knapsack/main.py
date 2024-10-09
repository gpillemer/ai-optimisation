import inspect
import streamlit as st
import langroid as lr
import langroid.language_models as lm
import json
import pandas as pd
import re
from solver import Solver
from prompt import SYSTEM_PROMPT_TEMPLATE, DATA_SUMMARISER_SYSTEM_MESSAGE

# Set up LLM
llm_cfg = lm.OpenAIGPTConfig(
    chat_model="litellm/claude-3-5-sonnet-20240620",
    chat_context_length=8000, # adjust according to model
)

# Use LLM in an Agent
agent_cfg = lr.ChatAgentConfig(llm=llm_cfg)
agent = lr.ChatAgent(agent_cfg)

# Use LLM in an Agent
data_agent = lr.ChatAgent(agent_cfg)

class ConstraintInterpreter(lr.Task):
    def __init__(self, agent, name, system_message):
        super().__init__(agent, name=name, system_message=system_message)

    def run(self, user_message):
        if not user_message.strip():
            return [], "No constraints provided."
        
        response = self.agent.llm_response(user_message)
        
        # Extract constraint blocks
        constraint_blocks = re.findall(r'"""(.*?)"""', response.content, re.DOTALL)
        
        # Clean up the extracted constraints
        constraints = [constraint.strip() for constraint in constraint_blocks]
        
        # Extract the explanation part (everything before the first constraint block)
        explanation = response.content.split('"""')[0].strip() if '"""' in response.content else response.content
        
        if not constraints:
            explanation += "\n\nNo valid constraints were extracted from the response."
        
        return constraints, explanation
    
class DataSummariser(lr.Task):
    def __init__(self, agent, name, system_message):
        super().__init__(agent, name=name, system_message=system_message)

    def run(self, json_data):
        response = self.agent.llm_response(json_data)
        return response.content

st.session_state.data_summariser = DataSummariser(
                data_agent, 
                name="DataSummariser", 
                system_message=DATA_SUMMARISER_SYSTEM_MESSAGE
            )

if 'json_data' not in st.session_state:
    st.session_state.json_data = None

if 'items_df' not in st.session_state:
    st.session_state.items_df = None

if 'max_weight_df' not in st.session_state:
    st.session_state.max_weight_df = None

if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Upload"

if 'solution' not in st.session_state:
    st.session_state.solution = None

if 'constraints' not in st.session_state:
    st.session_state.constraints = []

if 'explanation' not in st.session_state:
    st.session_state.explanation = ""

# Streamlit app
def main():
    st.title("Knapsack Problem Solver")

    # Radio buttons for tab selection
    st.session_state.current_tab = st.radio("Select Tab:", ["Upload", "Input", "Results"], index=["Upload", "Input", "Results"].index(st.session_state.current_tab))

    if st.session_state.current_tab == "Upload":
        handle_upload_tab()
    elif st.session_state.current_tab == "Input":
        handle_input_tab()
    elif st.session_state.current_tab == "Results":
        handle_results_tab()

def handle_upload_tab():
    st.header("Upload Data")
    
    uploaded_file = st.file_uploader("Choose a JSON file", type="json")

    if st.button("Read Data"):
        if uploaded_file is not None:
            st.session_state.json_data = json.load(uploaded_file)
            st.session_state.items_df = pd.DataFrame(st.session_state.json_data['items'])
            if 'max_weight' in st.session_state.json_data:
                st.session_state.max_weight_df = pd.DataFrame([{"max_weight": st.session_state.json_data['max_weight']}])
            else:
                st.session_state.max_weight_df = pd.DataFrame([{"max_weight": float('inf')}])
            st.success("Data read successfully. Switching to Input tab.")
            st.session_state.current_tab = "Input"
            data_summary = st.session_state.data_summariser.run(json.dumps(st.session_state.json_data))
            model_code = inspect.getsource(Solver)
            # Initialize session state
            st.session_state.constraint_interpreter = ConstraintInterpreter(
                agent, 
                name="ConstraintBot", 
                system_message=SYSTEM_PROMPT_TEMPLATE.format(data_summary=data_summary, model_code=model_code)
            )
            st.rerun()
        else:
            st.error("Please upload a JSON file before reading data.")

def handle_input_tab():
    st.header("Edit Data and Optimize")
    
    if st.session_state.items_df is not None and st.session_state.max_weight_df is not None:
        st.subheader("Items")
        edited_items_df = st.data_editor(st.session_state.items_df, num_rows="dynamic")
        
        st.subheader("Maximum Weight")
        edited_max_weight_df = st.data_editor(
            st.session_state.max_weight_df, 
            num_rows="fixed",
            hide_index=True
        )

        user_message = st.text_area("Enter business rules for constraints (optional):")

        if st.button("Interpret Constraints and Optimize"):
            # Interpret constraints
            st.session_state.constraints, st.session_state.explanation = st.session_state.constraint_interpreter.run(user_message)

            # Update the json_data with edited values
            st.session_state.json_data = {
                'items': edited_items_df.to_dict('records'),
                'max_weight': edited_max_weight_df['max_weight'].iloc[0]
            }

            # Solve the knapsack problem
            solver = Solver(st.session_state.json_data['items'], st.session_state.json_data['max_weight'], st.session_state.constraints)
            solver.solve()
            st.session_state.solution = solver.get_results()

            st.success("Optimization complete. Switching to Results tab.")
            st.session_state.current_tab = "Results"
            st.rerun()
    else:
        st.info("No data available. Please upload and read data in the Upload tab first.")

def handle_results_tab():
    st.header("Results and Re-Optimize")
    
    if st.session_state.solution:
        selected_items, total_value, total_weight = st.session_state.solution
        if selected_items:
            st.subheader("Selected Items")
            selected_items_df = pd.DataFrame(selected_items)
            st.dataframe(selected_items_df.set_index('id'))
            st.write(f"Total Value: {total_value:.2f}")
            st.write(f"Total Weight: {total_weight:.2f}")
            st.write(f"Number of items selected: {len(selected_items)}")

        st.subheader("Constraint Interpretation and Explanation")
        st.write(st.session_state.explanation)

        st.subheader("Applied Constraints")
        for i, constraint in enumerate(st.session_state.constraints):
            st.code(constraint, language="python")

        follow_up_message = st.text_area("Enter additional business rules for constraints (optional):")

        if st.button("Interpret New Constraints and Re-Optimize"):
            # Interpret new constraints
            new_constraints, new_explanation = st.session_state.constraint_interpreter.run(follow_up_message)
            st.session_state.constraints.extend(new_constraints)
            st.session_state.explanation += "\n\nAdditional Explanation:\n" + new_explanation

            # Re-solve the knapsack problem
            solver = Solver(st.session_state.json_data['items'], st.session_state.json_data['max_weight'], st.session_state.constraints)
            solver.solve()
            st.session_state.solution = solver.get_results()

            st.success("Re-optimization complete.")
            st.rerun()
    else:
        st.info("No results yet. Please optimize in the Input tab first.")

if __name__ == "__main__":
    main()