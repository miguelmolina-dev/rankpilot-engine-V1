from langgraph.graph import StateGraph, END
from src.graph.state import RankPilotState
from src.agents.structural_analyzer import structural_analyzer_node
from src.agents.interrogator import interrogator_node
from src.agents.snapshot_generator import snapshot_generator_node
from src.agents.scheduler import scheduler_node
from src.agents.executive_writer import executive_writer_node

def create_rankpilot_workflow():
    """
    Initializes the LangGraph StateMachine with Parallel Strategic Nodes.
    """
    workflow = StateGraph(RankPilotState)

    # 1. Add Atomic Nodes
    workflow.add_node("analyze_structure", structural_analyzer_node)
    workflow.add_node("interrogate", interrogator_node)
    
    # --- Parallel Nodes (Fan-out) ---
    workflow.add_node("generate_snapshot", snapshot_generator_node) # The Auditor
    workflow.add_node("strategic_scheduler", scheduler_node) # The Architect
    
    # --- Synthesis Node (Fan-in) ---
    workflow.add_node("executive_writer", executive_writer_node) # The Voice

    # 2. Define Entry Point (Conditional to allow resuming)
    def entry_router(state: RankPilotState):
        if state.current_step > 0:
            return "interrogate"
        return "analyze_structure"

    workflow.set_conditional_entry_point(
        entry_router,
        {
            "analyze_structure": "analyze_structure",
            "interrogate": "interrogate"
        }
    )

    # 3. Define Linear Edges
    workflow.add_edge("analyze_structure", "interrogate")

    # 4. Define Interrogation Loop (Conditional)
    def route_interrogation(state: RankPilotState):
        if state.next_node == "generate_snapshot":
            return "generate_snapshot"
        # Return END to interrupt the flow and send state back to Laravel
        return END

    workflow.add_conditional_edges(
        "interrogate",
        route_interrogation,
        {
            "generate_snapshot": "generate_snapshot",
            END: END
        }
    )

    # 5. Define Fan-in (Wait for both parallel nodes to finish)
    workflow.add_edge("generate_snapshot", "strategic_scheduler") # Architect second
    workflow.add_edge("strategic_scheduler", "executive_writer") # Writer last

    # 6. Define End Point
    workflow.add_edge("executive_writer", END)

    return workflow.compile()

app_workflow = create_rankpilot_workflow()