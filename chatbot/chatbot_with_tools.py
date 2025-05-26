from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, add_messages
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_community.tools import TavilySearchResults
from langgraph.prebuilt import ToolNode

load_dotenv()

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)

search_tool = TavilySearchResults()

llm_with_tools = llm.bind_tools([search_tool])

def chatbot(state: ChatState) -> ChatState:
    ai_message = llm_with_tools.invoke(state['messages'])
    return {
        'messages': [ai_message]
    }

def tools_router(state):
    last_message = state['messages'][-1]
    if hasattr(last_message, 'tool_calls') and len(last_message.tool_calls) > 0:
        return 'tool_node'
    return END

tools_node = ToolNode(tools=[search_tool], messages_key='messages')

graph = StateGraph(ChatState)
graph.add_node("chatbot", chatbot)
graph.add_node("tool_node", tools_node)
graph.set_entry_point("chatbot")

graph.add_conditional_edges('chatbot', tools_router)
graph.add_edge("tool_node", "chatbot")

app = graph.compile()

while True:
    input_text = input("You: ")
    if input_text.lower() in ['exit', 'quit']:
        break
    else:
        result = app.invoke({'messages': [HumanMessage(content=input_text)]})
        print("Chatbot:", result)  # Print the chatbot's response