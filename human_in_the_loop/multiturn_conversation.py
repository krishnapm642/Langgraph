from langgraph.graph import StateGraph, END, add_messages, START
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
import uuid

load_dotenv()   

class State(TypedDict):
    linked_topic : str
    human_messages : Annotated[List[str], add_messages]
    generated_post : Annotated[List[BaseMessage], add_messages]

def model(state: State):
    '''Here we are generating the linkedIn post with Human feedback Incorporated'''

    print("Generating LinkedIn post based on the topic and human messages...")
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
    linked_topic = state['linked_topic']
    human_messages = state['human_messages'] if 'human_messages' in state else ["No feedback found"]
    
    prompt = f"""
    LinkedIn Topic: {linked_topic}
    Human Feedback: {human_messages[-1] if human_messages else "No feedback provided"}
    Generate a structured and well written LinkedIn post maximum of 5 lines based on the above topic
    Consider the human feedback to improve the post quality"""
    response = llm.invoke([
        SystemMessage(content="You are a expert LinkedIn post generator."),
        HumanMessage(content=prompt)
    ])

    generated_linked_in_post = response.content

    print("Generated LinkedIn post:", generated_linked_in_post)

    return {
        'human_messages': human_messages,
        'generated_post': [AIMessage(content=generated_linked_in_post)]
    }

def human_node(state: State):
    ''''Human intervention Node: Loops back to generate node untill the input is done'''

    print("Human feedback Node, Awaiting for the human response.")

    generated_post = state['generated_post']

    user_feedback = interrupt(
        {
            'generated_post': generated_post,
            'message': "Provide feedback or write 'done' to finish the post."
        }
    )

    print("User feedback received [human node]:", user_feedback)

    if user_feedback.lower() == 'done':
        return Command(goto='end_node', update={'human_messages': state['human_messages'] + ['Post finalized by human.']
        })
    return Command(goto='model', update={'human_messages': state['human_messages'] + [user_feedback]})


def end_node(state: State):
    '''Final node to print the post and end the conversation'''
    print("Post finalized and published!")
    generated_post = state['generated_post'][-1]
    print(f"The final LinkedIn post is:\n{generated_post}")
    return {'generated_post': state['generated_post'], 'human_messages': state['human_messages']}


graph = StateGraph(State)
graph.add_node("model", model)
graph.add_node("end_node", end_node)
graph.add_node("human_node", human_node)

graph.set_entry_point("model")

# defining the flow
graph.add_edge(START, "model")
graph.add_edge("model", "human_node")

graph.set_finish_point("end_node")

# interrupt mechanism
checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)


thread_config = {"configurable": {"thread_id": uuid.uuid4()}}

linked_in_topic = input("Enter the LinkedIn topic for the post: ")
initial_state = {
    'linked_topic': linked_in_topic,
    'human_messages': [],
    'generated_post': []
}

for chunk in app.stream(initial_state, config=thread_config):
    for node_id, value in chunk.items():
        #  If we reach an interrupt, continuously ask for human feedback

        if(node_id == "__interrupt__"):
            while True: 
                user_feedback = input("Provide feedback (or type 'done' when finished): ")

                # Resume the graph execution with the user's feedback
                app.invoke(Command(resume=user_feedback), config=thread_config)

                # Exit loop if user says done
                if user_feedback.lower() == "done":
                    break