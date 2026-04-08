from typing import Annotated, TypedDict, List, Dict, Optional
from langgraph.graph.message import add_messages
from operator import add
from pydantic import BaseModel

# Matches CorePositioning in snapshot_chain.py
class PositioningCore(BaseModel):
    practice_model: str  
    practice_definition: str  
    confidence_score: float
    signals: List[str]

class PositioningTier(BaseModel):
    label: str
    explanation: str

class BlindSpot(BaseModel):
    issue: str
    description: str

class EvolutionAction(BaseModel):
    action: str
    impact: str
    instruction: str

class NewAnswer(BaseModel):
    question_text: str
    answer: str

class MetaData(BaseModel):
    file_base64: str
    directory: Optional[str]
    current_band: Optional[str]
    target_band: Optional[str]

class RankPilotState(BaseModel):
    submission_id: str
    metadata: Optional[MetaData] = None
    raw_text: str  
    new_answer: Optional[NewAnswer] = None
    history: List[str] = []
    current_step: int = 0
    gaps: Optional[List[str]] = None
    positioning_core: Optional[PositioningCore] = None
    positioning_tier: Optional[PositioningTier] = None
    blind_spots: List[BlindSpot] = []
    competitive_advantage: List[str] = []
    evolution_path: List[EvolutionAction] = []
    next_node: str = ""