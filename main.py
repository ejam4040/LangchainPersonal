from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from typing import TypedDict
import random
from typing import Literal
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
import subprocess
import os
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langgraph.graph import MessagesState


class State(TypedDict):
  graph_state: str


def node_1(state):
  print("---Node 1---")
  return {"graph_state": state['graph_state'] + " I am"}


def node_2(state):
  print("---Node 2---")
  return {"graph_state": state['graph_state'] + " happy!"}


def node_3(state):
  print("---Node 3---")
  return {"graph_state": state['graph_state'] + " sad!"}


def decide_mood(state) -> Literal["node_2", "node_3"]:
  # Often, we will use state to decide on the next node to visit
  user_input = state['graph_state']

  # Here, let's just do a 50 / 50 split between nodes 2, 3
  if random.random() < 0.5:
    # 50% of the time, we return Node 2
    return "node_2"

  # 50% of the time, we return Node 3
  return "node_3"

def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b  

llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools([multiply])    

# Node
def tool_calling_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


def main():

  

  # Node
  def tool_calling_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

  # Build graph
  builder = StateGraph(MessagesState)
  builder.add_node("tool_calling_llm", tool_calling_llm)
  builder.add_node("tools", ToolNode([multiply]))
  builder.add_edge(START, "tool_calling_llm")
  builder.add_conditional_edges(
    "tool_calling_llm",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
  )
  builder.add_edge("tools", END)
  graph = builder.compile()

  # View
  display(Image(graph.get_graph().draw_mermaid_png()))

 
if __name__ == "__main__":
  main()
