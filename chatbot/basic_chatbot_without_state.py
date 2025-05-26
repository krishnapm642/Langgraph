from langgraph.graph import StateGraph, END, add_messages
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
import operator

load_dotenv()

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)

graph = StateGraph(ChatState)

def chatbot(state : ChatState) -> ChatState:
    """
    A simple chatbot function that returns the last message in the chat history.
    """
    ai_message = llm.invoke(state['messages'])
    return {
        'messages': [ai_message]
    }

graph.add_node("chatbot", chatbot)  
graph.set_entry_point("chatbot")
graph.add_edge("chatbot", END)
app = graph.compile()

while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit', 'quit']:
        break
    else:
        result = app.invoke({'messages': [HumanMessage(content=user_input)]})
        print("Chatbot:", result)  # Print the chatbot's response