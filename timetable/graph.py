from typing import Annotated, List, Optional, Type, Literal

from typing_extensions import TypedDict
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool
from langchain_core.globals import set_debug, set_verbose

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langgraph.checkpoint.memory import MemorySaver

from timetable.model import create_and_solve_timetable_model


set_debug(False)
set_verbose(False)

memory = MemorySaver()


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)




# Define the literal types
ClassLiteral = Literal["C1", "C2", "C3", "C4", "C5"]
TimeSlotLiteral = Literal["T1", "T2", "T3", "T4", "T5"]
TeacherLiteral = Literal["Teacher1", "Teacher2", "Teacher3", "Teacher4"]
ClassroomLiteral = Literal["Room1", "Room2", "Room3", "Room4"]

class ClassTeacherMapping(BaseModel):
    classId: ClassLiteral
    teacher: TeacherLiteral

class ClassRoomMapping(BaseModel):
    classId: ClassLiteral
    room: ClassroomLiteral

class ForcedAssignment(BaseModel):
    classId: ClassLiteral
    timeslot: TimeSlotLiteral

class Constraints(BaseModel):
    OneTimeSlotPerClass: bool
    TeacherConflict: bool
    RoomConflict: bool

class TimetableInput(BaseModel):
    Classes: List[ClassLiteral]
    TimeSlots: List[TimeSlotLiteral]
    Teachers: List[TeacherLiteral]
    Classrooms: List[ClassroomLiteral]
    ClassTeacherMapping: List[ClassTeacherMapping]
    ClassRoomMapping: List[ClassRoomMapping]
    Constraints: Constraints
    ForcedAssignments: Optional[List[ForcedAssignment]] = None

class TimetableInputSchema(BaseModel):
    input: TimetableInput

class TimetableOptimiserTool(BaseTool):
    name = "time_table_optimiser"
    description = "Optimise the timetable"
    args_schema: Type[BaseModel] = TimetableInputSchema

    def _run(
        self, input: TimetableInput
    ) -> str:
        """Use the tool."""
        data = input.model_dump()
        return create_and_solve_timetable_model(data)


tools = [TimetableOptimiserTool()]
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")
graph = graph_builder.compile(checkpointer=memory)

if __name__ == "__main__":
    while True:
        config = {"configurable": {"thread_id": "1"}}
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        for event in graph.stream({"messages": ("user", user_input)}, config=config):
            for value in event.values():
                print("Assistant:", value["messages"][-1].content)
