from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm_manager import get_llm
from pydantic import BaseModel, Field
from typing import List
from langchain_core.output_parsers import PydanticOutputParser

# 1. Nested Schemas for precise JSON structure
class PracticeModel(BaseModel):
    label: str = Field(description="The formal name of the practice type.")
    definition: str = Field(description="A concise technical definition.")

class PositioningTier(BaseModel):
    label: str = Field(description="One of: 'Elite', 'Consolidated', or 'Market Member'.")
    explanation: str = Field(description="Professional justification for the assigned tier.")

class BlindSpot(BaseModel):
    issue: str = Field(description="A short title for the identified gap.")
    description: str = Field(description="A detailed explanation of why this is a risk.")

class CorePositioning(BaseModel):
    # Antes era: practice_model: str
    practice_model: PracticeModel = Field(description="The formal name and technical definition.")
    confidence_score: float = Field(description="Value between 0.0 and 1.0.")
    signals: List[str] = Field(description="Exactly 3 specific evidence-backed signals.")

class FinalSnapshot(BaseModel):
    """
    Ensure the top-level keys match what the Snapshot Node expects.
    """
    practice_model: PracticeModel = Field(description="The formal name and technical definition.")
    positioning_tier: PositioningTier = Field(description="Elite, Consolidated, or Market Member.")
    confidence_score: float = Field(description="Value between 0.0 and 1.0.")
    positioning_core: CorePositioning = Field(description="The full technical audit data for the Snapshot Node.")
    signals: List[str] = Field(description="Exactly 3 specific evidence-backed signals.")
    blind_spots: List[BlindSpot] = Field(description="Exactly 4 high-stakes technical gaps.")
    # Fix the typo: 'competitive_advantages' (plural) to match your state if needed
    competitive_advantage: List[str] = Field(description="Top 2 'Elite' signals.")

parser = PydanticOutputParser(pydantic_object=FinalSnapshot)

snapshot_prompt = ChatPromptTemplate.from_template(
    """
    SYSTEM: 
    You are the "Lead Auditor" for Global Legal Rankings. You are cold, analytical, and impossible to impress. 
    Your mission is to strip away the marketing fluff and expose the raw technical standing of this submission.
    
    GROUNDING MANDATE: 
    If it is not in the {raw_text} or {history}, it DOES NOT EXIST. 
    Do not hallucinate complexity. If the submission is weak, label it as 'Market Member' without hesitation.

    AUDIT PARAMETERS:
    - Practice Area: {practice_area}
    - Submission Evidence: {raw_text}
    - Supplemental Evidence: {history}
    - Gaps Identified: {gaps}

    PHASE 1: THE TECHNICAL CORE
    - Define the 'Practice Model' based on the complexity of matters. 
    - Is this 'High-End Specialty', 'Commoditized Service', or 'Strategic Advisory'?

    PHASE 2: THE TIER VERDICT
    - Assign a Tier: [Elite / Consolidated / Market Member].
    - JUSTIFICATION: Compare the evidence against Band 1 standards for {practice_area}. 
    - If there is a 'Key Man Risk' (all cases lead by one person), downgrade the tier.

    PHASE 3: THE INVISIBLE RISKS (4 Blind Spots)
    Identify exactly 4 technical gaps that an investigator would use to reject a Band 1 ranking.
    Focus on: 
    1. Lack of Quantitative Depth (Missing $$$ values).
    2. Missing Market-Leading Friction (Standard vs. Complex cases).
    3. Low Peer Recognition Signals.
    4. Weak Narrative Cohesion.

    PHASE 4: THE WEAPONS (2 Competitive Advantages)
    Identify exactly 2 reasons why this firm is a threat to the market. 
    Look for: Unique regulatory access, specific landmark precedents, or niche dominance.

    TONE: 
    Surgical, objective, and authoritative. Use the exact names of Partners and Matters to anchor your findings.
    
    {format_instructions}
    """
)

llm = get_llm(temperature=0.2)
snapshot_chain = (
    snapshot_prompt.partial(format_instructions=parser.get_format_instructions())
    | llm
    | parser
)