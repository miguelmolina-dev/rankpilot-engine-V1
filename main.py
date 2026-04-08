from fastapi import FastAPI, HTTPException
from src.graph.workflow import app_workflow
from src.graph.state import RankPilotRequest

app = FastAPI(title="RankPilot Engine")

@app.post("/process")
async def process_submission(request: RankPilotRequest):
    try:
        # Invocamos el grafo - Since RankPilotState is now a BaseModel, we can pass it directly
        final_state = app_workflow.invoke(request)
        return final_state
    except Exception as e:
        print(f"!!! Error en el flujo: {e}")
        raise HTTPException(status_code=500, detail=str(e))