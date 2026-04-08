from fastapi import FastAPI, HTTPException
from src.graph.workflow import app_workflow
from src.graph.state import RankPilotState

app = FastAPI(title="RankPilot Engine")

@app.post("/process")
async def process_submission(state: RankPilotState):
    """
    The main endpoint for Laravel. 
    Receives the current state, runs one 'turn' of the graph, and returns the update. [cite: 5, 6]
    """
    # LangGraph will start from the 'next_node' specified in the state 
    # and run until it hits a breakpoint or a node that returns a state update. [cite: 50, 53]
    try:
        result = app_workflow.invoke(state)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))