from fastapi import FastAPI, HTTPException
from src.graph.workflow import app_workflow
from src.graph.state import RankPilotRequest

app = FastAPI(title="RankPilot Engine")

@app.post("/process")
async def process_submission(request: RankPilotRequest):
    try:
        # model_dump() crea el diccionario que RankPilotState espera
        state_dict = request.model_dump()
        
        # Invocamos el grafo
        final_state = app_workflow.invoke(state_dict)
        return final_state
    except Exception as e:
        print(f"!!! Error en el flujo: {e}")
        raise HTTPException(status_code=500, detail=str(e))