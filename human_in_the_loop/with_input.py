from langgraph.graph import StateGraph, END, add_messages
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import TypedDict, Annotated

load_dotenv()

POST = "post"
COLLECT_FEEDBACK = "collect_feedback"
GENERATE_POST = "generate_post"
GET_REVIEW_DECISION = "get_review_decision"


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def generate_post(state: State) -> State:
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
    ai_message = llm.invoke(state['messages'])
    return {
        'messages': [ai_message]
    }

def get_review_decision(state: State) -> State:
    post_content = state["messages"][-1].content

    print("Current post content: \n", post_content)

    decision = input("Do you approve this post? (yes/no): ").strip().lower()

    if decision == 'yes':
        return POST
    return COLLECT_FEEDBACK

def collect_feedback(state: State) -> State:
    feedback = input("Please provide your feedback on the post")
    message = HumanMessage(content=feedback)
    return {
        'messages': [message]
    }

def post(state: State) -> State:
    print("Post approved and published!")
    print(f"the final post is :\n {state['messages'][-1].content}")


graph = StateGraph(State)
graph.add_node(GENERATE_POST, generate_post)
graph.add_node(GET_REVIEW_DECISION, get_review_decision)
graph.add_node(COLLECT_FEEDBACK, collect_feedback)
graph.add_node(POST, post)

graph.set_entry_point(GENERATE_POST)

graph.add_conditional_edges(GENERATE_POST, get_review_decision)
graph.add_edge(POST, END)
graph.add_edge(COLLECT_FEEDBACK, GENERATE_POST)

app = graph.compile()

response = app.invoke({
    "messages": [HumanMessage(content="Write me a LinkedIn post on AI Agents taking over content creation")]
})

print(response)