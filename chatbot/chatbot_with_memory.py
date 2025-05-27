from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END, add_messages
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3


load_dotenv()
sqlite_connection = sqlite3.connect('chat_memory.db', check_same_thread=False)
memory = SqliteSaver(sqlite_connection)

class BasicChatState(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages]

def chatbot(state : BasicChatState) -> BasicChatState:
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
    ai_message = llm.invoke(state['messages'])
    return {
        'messages': [ai_message]
    }

config = {
    'configurable': {
        'thread_id': 1
    }
}

graph = StateGraph(BasicChatState)

graph.add_node("chatbot", chatbot)
graph.set_entry_point("chatbot")
graph.add_edge("chatbot", END)

app = graph.compile(checkpointer=memory)

while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit', 'quit']:
        break
    else:
        response = app.invoke(
            {
                'messages': [HumanMessage(content=user_input)]
            }, config=config)
        print("Chatbot:", response['messages'][-1].content)
        