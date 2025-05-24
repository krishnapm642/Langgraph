from typing import TypedDict
from langgraph.graph import END, StateGraph


class CountState(TypedDict):
    count : int

def increment(state : CountState) -> CountState:
    return {'count' : state['count'] + 1}


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

