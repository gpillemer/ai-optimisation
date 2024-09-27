from typing import Annotated, List, Optional, Type, Literal
import json
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Union, Optional
import uuid
import os

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool
from langchain_core.globals import set_debug, set_verbose

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate

from generic.prompt import create_and_solve_generic_model, prompt_template, math_equation_prompt_template

set_debug(True)
set_verbose(True)

memory = MemorySaver()


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


class Variable(BaseModel):
    indices: Optional[Dict[str, str]] = None
    type: Literal["Binary", "Integer", "Continuous"]
    lower_bound: Union[int, float] = Field(default=0)
    upper_bound: Union[int, float, Literal["GRB.INFINITY"]] = Field(default="GRB.INFINITY")

class Objective(BaseModel):
    sense: Literal["minimize", "maximize"]
    expression: str

class Constraint(BaseModel):
    indices: Optional[Dict[str, str]] = None
    expression: str

ParameterValue = Union[int, float, Dict[str, Union[None,int, float,str, Dict[str, Union[int, float, None,str]]]]]

class GenericModelDataInput(BaseModel):
    model_name: str
    sets: Dict[str, List[Union[str, int]]]
    parameters: Dict[str, ParameterValue]
    variables: Dict[str, Variable]
    objective: Objective
    constraints: Dict[str, Constraint]

class GenericModelOptimiserSchema(BaseModel):
    input: GenericModelDataInput

    def __init__(self, **data):
        # Dump the input data to JSON before validation
        with open(os.path.join("session",f"data-{uuid.uuid4()}.json"), "w") as f:
            json.dump(data, f)
        # Call the original `__init__` method to continue the validation
        super().__init__(**data)

class GenericModelOptimiserTool(BaseTool):
    name = "generic_model_optimiser"
    description = "Optimise a generic model"
    args_schema: Type[BaseModel] = GenericModelOptimiserSchema

    def _run(
        self, input: GenericModelDataInput
    ) -> str:
        """Use the tool."""
        data = input.model_dump()
        return create_and_solve_generic_model(data)

# llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
llm = ChatOpenAI(model="gpt-4o")

model_equation_chain = math_equation_prompt_template | llm

model_equation_tool = model_equation_chain.as_tool(
    name="model_equation_tool",
    description="Use the model equation tool when first given a problem statement to generate the model equations",

)
tools = [GenericModelOptimiserTool(), model_equation_tool]
llm_with_tools = llm.bind_tools(tools)

chain = prompt_template | llm_with_tools


def chatbot(state: State):
    return {"messages": [chain.invoke(state["messages"])]}

# def model_equation(state: State):
#     return {"messages": [model_equation_chain.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
# graph_builder.add_node("model_equation", model_equation)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)

graph_builder.add_edge("tools", "chatbot")
# graph_builder.add_edge("model_equation", "chatbot")
# graph_builder.add_edge("chatbot", "model_equation")

graph_builder.set_entry_point("chatbot")
graph = graph_builder.compile(checkpointer=memory)

from IPython.display import Image, display

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass

def main():
    while True:
        config = {"configurable": {"thread_id": "1"}}
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        for event in graph.stream({"messages": ("user", user_input)}, config=config):
            for value in event.values():
                print("Assistant:", value["messages"][-1].content)



if __name__ == "__main__":
    main()



# d = '{"input": {"model_name": "BIM_Microchip_Production", "sets": {"Chips": ["Logic", "Memory"], "Materials": ["Silicon", "Germanium", "Plastic", "Copper"]}, "parameters": {"Profit": {"Logic": 12, "Memory": 9}, "Usage": {"Silicon": {"Logic": 1, "Memory": 0}, "Germanium": {"Logic": 0, "Memory": 1}, "Plastic": {"Logic": 1, "Memory": 1}, "Copper": {"Logic": 4, "Memory": 2}}, "Stock": {"Silicon": 1000, "Germanium": 1500, "Plastic": 1750, "Copper": 4800}}, "variables": {"x": {"indices": {"i": "Chips"}, "type": "Integer", "lower_bound": 0}}, "objective": {"sense": "maximize", "expression": \"gp.quicksum(variables["x"][i] * parameters["Profit"][i] for i in sets["Chips"])\"}, "constraints": {"MaterialConstraint": {"indices": {"m": "Materials"}, "expression": \"gp.quicksum(variables["x"][i] * parameters["Usage"][m][i] for i in sets["Chips"]) <= parameters["Stock"][m]\"}}}}'

# import json

# dt = json.loads(d)


# dt = {
#   "model_name": "BIM_Microchip_Production",
#   "sets": {
#     "Chips": [
#       "Logic",
#       "Memory"
#     ],
#     "Materials": [
#       "Silicon",
#       "Germanium",
#       "Plastic",
#       "Copper"
#     ]
#   },
#   "parameters": {
#     "Profit": {
#       "Logic": 12,
#       "Memory": 9
#     },
#     "Usage": {
#       "Silicon": {
#         "Logic": 1,
#         "Memory": 0
#       },
#       "Germanium": {
#         "Logic": 0,
#         "Memory": 1
#       },
#       "Plastic": {
#         "Logic": 1,
#         "Memory": 1
#       },
#       "Copper": {
#         "Logic": 4,
#         "Memory": 2
#       }
#     },
#     "Stock": {
#       "Silicon": 1000,
#       "Germanium": 1500,
#       "Plastic": 1750,
#       "Copper": 4800
#     }
#   },
#   "variables": {
#     "x": {
#       "indices": {
#         "i": "Chips"
#       },
#       "type": "Integer",
#       "lower_bound": 0
#     }
#   },
#   "objective": {
#     "sense": "maximize",
#     "expression": "gp.quicksum(variables['x'][i] * parameters['Profit'][i] for i in sets['Chips'])"
#   },
#   "constraints": {
#     "MaterialConstraint": {
#       "indices": {
#         "m": "Materials"
#       },
#       "expression": "gp.quicksum(variables['x'][i] * parameters['Usage'][m][i] for i in sets['Chips']) <= parameters['Stock'][m]"
#     }
#   }
# }

# GenericModelDataInput(**dt)