from typing import Annotated, List, Dict, Optional
from pydantic import BaseModel, Field

print("State module loaded successfully.")

# Matches CorePositioning in snapshot_chain.py
class PositioningCore(BaseModel):
    practice_model: str = ""
    practice_definition: str = ""
    confidence_score: float = 0.0
    signals: List[str] = Field(default_factory=list)

class PositioningTier(BaseModel):
    label: str = ""
    explanation: str = ""

class BlindSpot(BaseModel):
    issue: str = ""
    description: str = ""

class EvolutionAction(BaseModel):
    action: str = ""
    impact: str = ""
    instruction: str = ""

class NewAnswer(BaseModel):
    question_text: str = ""
    answer: str = ""

class MetaData(BaseModel):
    file_path: str = ""
    directory: Optional[str] = None
    current_band: Optional[str] = None
    target_band: Optional[str] = None

class RankPilotState(BaseModel):
    # --- Metadata & Input ---
    submission_id: str = ""
    metadata: Optional[MetaData] = None
    raw_text: str = ""
    file_content: Optional[Dict] = None
    
    # --- Interrogation History ---
    new_answer: Optional[NewAnswer] = None
    history: List[str] = Field(default_factory=list)
    current_step: int = 0

    gaps: Optional[List[str]] = None
    
    # --- Analysis Results ---
    positioning_core: Optional[PositioningCore] = None
    positioning_tier: Optional[PositioningTier] = None
    
    # --- Results Fields ---
    blind_spots: List[BlindSpot] = Field(default_factory=list)
    competitive_advantage: List[str] = Field(default_factory=list)
    evolution_path: List[EvolutionAction] = Field(default_factory=list)
    
    # --- Flow Control ---
    next_node: str = ""

    model_config = {"extra": "allow"}
