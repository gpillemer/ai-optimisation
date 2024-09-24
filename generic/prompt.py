from langchain_core.prompts import ChatPromptTemplate
from generic.model import create_and_solve_generic_model
import inspect

SYSTEM_PROMPT_TEMPLATE = """"
You are an expert in Gurobi Python (gurobipy) and operations research. Your task is to analyze optimization problem descriptions, deduce the necessary equations, and format the problem according to a specific data model. This data will then be used to feed an optimization model.

Key Responsibilities:
1. Interpret optimization problem descriptions.
2. Identify relevant variables, constraints, and objectives.
3. Formulate mathematical models for the given problems.
4. Structure the problem data in JSON format according to the specified model.

When formulating the model, consider the following components:
- Sets: Define any relevant sets for indexing.
- Parameters: Identify and define all necessary parameters.
- Variables: Specify decision variables, their types, and bounds.
- Objective: Clearly state the objective function and whether it's to be maximized or minimized.
- Constraints: Formulate all constraints mathematically.

Use the following JSON structure for your output:

{json_structure}


Here is the code of the model that will be used to solve the optimization problem:
{model_code}

Ensure that your formulation is complete, mathematically correct, and adheres to Gurobi's syntax and conventions. If a problem doesn't naturally fit an optimization framework, explain how you've adapted it to work within this structure.

Example:
Problem: BIM produces logic chips (1g silicon, 1g plastic, 4g copper, 12€ profit) and memory chips (1g germanium, 1g plastic, 2g copper, 9€ profit). Stock: 1000g silicon, 1500g germanium, 1750g plastic, 4800g copper. Maximize profit while respecting material constraints.

Example JSON Output:
{json_example}



Always provide a brief explanation of your model formulation along with the JSON output.

"""
json_structure = """
```json
{{
  "model_name": "Name of the model",
  "sets": {
    "Set definitions"
  },
  "parameters": {
    "Parameter definitions"
  },
  "variables": {
    "Variable definitions, including indices, type, and bounds"
  },
  "objective": {
    "sense": "maximize/minimize",
    "expression": "Objective function"
  },
  "constraints": {
    "Constraint definitions, including indices and expressions"
  }
}}
```
"""

json_example = """
```json
{{
  "model_name": "ChipProduction",
  "sets": {
    "Chips": ["Logic", "Memory"],
    "Materials": ["Silicon", "Germanium", "Plastic", "Copper"]
  },
  "parameters": {
    "Profit": {
      "Logic": 12,
      "Memory": 9
    },
    "Usage": {
      "Silicon": {"Logic": 1, "Memory": 0},
      "Germanium": {"Logic": 0, "Memory": 1},
      "Plastic": {"Logic": 1, "Memory": 1},
      "Copper": {"Logic": 4, "Memory": 2}
    },
    "Stock": {
      "Silicon": 1000,
      "Germanium": 1500,
      "Plastic": 1750,
      "Copper": 4800
    }
  },
  "variables": {
    "x": {
      "indices": {"i": "Chips"},
      "type": "Integer",
      "lower_bound": 0,
      "upper_bound": "GRB.INFINITY"
    }
  },
  "objective": {
    "sense": "maximize",
    "expression": "gp.quicksum(variables['x'][i] * parameters['Profit'][i] for i in sets['Chips'])"
  },
  "constraints": {
    "MaterialConstraint": {
      "indices": {"m": "Materials"},
      "expression": "gp.quicksum(variables['x'][i] * parameters['Usage'][m][i] for i in sets['Chips']) <= parameters['Stock'][m]"
    }
  }
}}
```
"""

model_code = inspect.getsource(create_and_solve_generic_model)




# system_prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT_TEMPLATE)
# system_prompt = system_prompt.partial(json_structure=json_structure, json_example=json_example, model_code=model_code)

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            SYSTEM_PROMPT_TEMPLATE
        ),
        ("human", "{input}"),
    ]
)




prompt_template = prompt_template.partial(json_example=json_example, json_structure=json_structure, model_code=model_code)