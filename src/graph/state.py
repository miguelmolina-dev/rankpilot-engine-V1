from typing import Annotated, TypedDict, List, Dict, Optional
from langgraph.graph.message import add_messages
from operator import add

# Matches CorePositioning in snapshot_chain.py
class PositioningCore(TypedDict):
    practice_model: str  
    practice_definition: str  
    confidence_score: float
    signals: List[str]

class PositioningTier(TypedDict):
    label: str
    explanation: str

class BlindSpot(TypedDict):
    issue: str
    description: str

class EvolutionAction(TypedDict):
    action: str
    impact: str
    instruction: str

class NewAnswer(TypedDict):
    question_text: str
    answer: str

class MetaData(TypedDict):
    file_path: str
    directory: Optional[str]
    current_band: Optional[str]
    target_band: Optional[str]

class RankPilotState(TypedDict):
    # --- Metadata & Input ---
    submission_id: str
    metadata: Optional[MetaData]
    raw_text: str  
    
    # --- Interrogation History ---
    new_answer: Optional[NewAnswer]
    history: List[str] 
    current_step: Annotated[int, add]

    gaps: Optional[List[str]]  # This can be a simple string for now, or a more complex structure later
    
    # --- Analysis Results ---
    positioning_core: Optional[PositioningCore]
    positioning_tier: Optional[PositioningTier]
    
    # --- Results Fields ---
    blind_spots: List[BlindSpot]
    competitive_advantage: List[str]
    evolution_path: List[EvolutionAction]
    
    # --- Flow Control ---
    next_node: str