from fastapi import FastAPI
from src.graph.workflow import app_workflow
from src.graph.state import RankPilotState

app = FastAPI(title="RankPilot Engine")

@app.post("/process")
async def process_state(state: RankPilotState):
    # Convertimos el modelo de Pydantic a un diccionario compatible con tus nodos
    state_dict = state.model_dump()
    
    # Ejecutamos el workflow
    final_state = app_workflow.invoke(state_dict)
    
    return final_state