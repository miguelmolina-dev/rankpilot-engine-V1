from langgraph.graph import StateGraph, END
from src.graph.state import RankPilotState
from src.agents.structural_analyzer import structural_analyzer_node
from src.agents.interrogator import interrogator_node
from src.agents.snapshot_generator import snapshot_generator_node

def create_rankpilot_workflow():
    """
    Initializes the LangGraph StateMachine for the RankPilot Engine.
    """
    # 1. Initialize the Graph with our Shared State
    workflow = StateGraph(RankPilotState)

    # 2. Add the Atomic Nodes
    workflow.add_node("analyze_structure", structural_analyzer_node)
    workflow.add_node("interrogate", interrogator_node)
    workflow.add_node("generate_snapshot", snapshot_generator_node)

    # 3. Define the Entry Point
    workflow.set_entry_point("analyze_structure") # We start with the structural analysis after ingestion

    # 4. Define the Transitions (Edges)
    
    # From Analysis, we ALWAYS go to Interrogation first
    workflow.add_edge("analyze_structure", "interrogate")

    # From Interrogation, we have a "Conditional Gate"
    # This checks the 'next_node' variable set by the Interrogator Agent
    def route_interrogation(state: RankPilotState):
        if state.get("next_node") == "generate_snapshot":
            return "generate_snapshot"
        return "interrogate" # This creates the loop for the 6 steps

    workflow.add_conditional_edges(
        "interrogate",
        route_interrogation,
        {
            "generate_snapshot": "generate_snapshot",
            "interrogate": "interrogate"
        }
    )

    # 5. Define the End Point
    workflow.add_edge("generate_snapshot", END)

    # 6. Compile the Graph
    return workflow.compile()

# This is what you will import in main.py
app_workflow = create_rankpilot_workflow()