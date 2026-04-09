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

class NewAnswer(TypedDict):
    question_text: str
    answer: str

class MetaData(TypedDict):
    file_base64: str = ""
    directory: Optional[str]
    current_band: Optional[str]
    target_band: Optional[str]
    region: str                 # e.g., "Latin America", "Europe"
    practice_area: str          # e.g., "Tax", "Banking & Finance"
    location: str             # e.g., "São Paulo", "New York"   
    submission_deadline: Optional[str]    # Format: YYYY-MM-DD
    firm_name: str

class Milestone(TypedDict):
    """Individual task in the strategic roadmap."""
    category: str           # "Strategic Narrative", "Quantitative Density", etc.
    action_title: str       # Short title for the Laravel UI
    why_it_matters: str     # The business value for the Partner
    technical_instruction: str # Detailed "How-to" for the lawyer
    priority_level: int     # 1 (Critical) to 5 (Low)
    days_before_deadline: int # Calculated days remaining until submission

class ExecutiveSummary(TypedDict):
    """Data for the Dynamic Dashboard and the Audit Letter."""
    overall_score: int          # 0-100 for the progress ring/chart
    risk_level: str             # "Critical", "Moderate", "Low"
    strategic_verdict: str      # A powerful 3-line impact paragraph
    top_differentiators: List[str] # Strongest points found in the PDF
    audit_letter_markdown: str  # Full body of the professional letter

class RankPilotState(TypedDict):
    # --- Metadata & Input ---
    submission_id: str
    metadata: Optional[MetaData]
    raw_text: Optional[str]
    
    # --- Interrogation History ---
    new_answer: Optional[NewAnswer]
    history: List[str] 
    current_step: int

    gaps: Optional[List[str]]  # This can be a simple string for now, or a more complex structure later
    
    # --- Analysis Results ---
    positioning_core: Optional[PositioningCore]
    positioning_tier: Optional[PositioningTier]
    
    # --- Results Fields ---
    blind_spots: List[BlindSpot]
    competitive_advantage: List[str]
    evolution_path: list[Milestone]

    #Executive Summary
    executive_summary: Optional[ExecutiveSummary]
    
    # --- Flow Control ---
    next_node: str