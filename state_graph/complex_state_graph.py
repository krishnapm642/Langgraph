from typing import TypedDict, List, Annotated
from langgraph.graph import END, StateGraph
import operator


class CountState(TypedDict):
    count : int
    sum : Annotated[int, operator.add]  # Using an operator to sum values
    history : Annotated[List[int], operator.concat]  # Using a list to keep track of history

def increment(state : CountState) -> CountState:
    new_count = state['count'] + 1
    return {
        'count': new_count,
        'sum': new_count,
        'history':[new_count]
    }


def should_continue(state: CountState):
    if state['count'] < 5:
        return 'continue'
    return 'stop'

graph = StateGraph(CountState)

graph.add_node('increment', increment)

graph.set_entry_point('increment')

graph.add_conditional_edges(
    'increment',
    should_continue,
    {
        'continue': 'increment',
        'stop': END
    }
)


app = graph.compile()
result = app.invoke({'count': 0})
print(result)

