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


def main():
  # Build graph
  builder = StateGraph(State)
  builder.add_node("node_1", node_1)
  builder.add_node("node_2", node_2)
  builder.add_node("node_3", node_3)

  # Logic
  builder.add_edge(START, "node_1")
  builder.add_conditional_edges("node_1", decide_mood)
  builder.add_edge("node_2", END)
  builder.add_edge("node_3", END)

  # Add
  graph = builder.compile()

  # View
  graph_image = graph.get_graph().draw_mermaid_png()
  display(Image(graph_image))

  # Save the image to a temporary file
  temp_file = "/tmp/graph_temp.png"
  with open(temp_file, "wb") as f:
    f.write(graph_image)

  # Try to display the image using different methods
  if os.environ.get('REPLIT_DB_URL'):  # Check if we're in Replit environment
    print("Running in Replit environment. Saving image to file.")
    output_file = "graph_output.png"
    with open(output_file, "wb") as f:
      f.write(graph_image)
    print(
        f"Image saved as {output_file}. You can view it in the file browser.")
  else:
    try:
      # First, try using imgcat
      subprocess.run(["imgcat", temp_file], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
      print(
          "imgcat not available. Trying to open the image with the default viewer."
      )
      try:
        # On macOS
        subprocess.run(["open", temp_file], check=True)
      except (subprocess.CalledProcessError, FileNotFoundError):
        try:
          # On Linux
          subprocess.run(["xdg-open", temp_file], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
          print(
              f"Unable to display the image. It has been saved as {temp_file}")

  # Clean up the temporary file
  os.remove(temp_file)

  graph.invoke({"graph_state": "Hi, this is Lance."})


if __name__ == "__main__":
  main()
