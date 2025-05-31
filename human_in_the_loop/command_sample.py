from langgraph.graph import StateGraph, END, add_messages
from langgraph.types import Command
from typing import TypedDict, Annotated


class State(TypedDict):
    messages: Annotated[list, add_messages]


def node_a(state: State) -> State:
    print("Node A executed")
    return Command(
        goto="node_b",
        update={
            'messages': ["Node A completed"]
        }
    )

def node_b(state: State) -> State:
    print("Node B executed")
    return Command(
        goto="node_c",
        update={
            'messages': ["Node B completed"]
        }
    )

def node_c(state: State) -> State:
    print("Node C executed")
    return Command(
        goto=END,
        update={
            'messages': ["Node c completed"]
        }
    )

graph = StateGraph(State)
graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)
graph.add_node("node_c", node_c)
graph.set_entry_point("node_a")
app = graph.compile()   

result = app.invoke({'messages': ["Starting the command sample"]})
print("Final messages:", result)