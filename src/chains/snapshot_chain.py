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

class EvolutionAction(BaseModel):
    action: str = Field(description="The title of the strategic move.")
    impact: str = Field(description="High, Medium, or Low.")
    instruction: str = Field(description="Practical 'how-to' for implementation.")

class CorePositioning(BaseModel):
    # Antes era: practice_model: str
    practice_model: PracticeModel = Field(description="The formal name and technical definition.")
    confidence_score: float = Field(description="Value between 0.0 and 1.0.")
    signals: List[str] = Field(description="Exactly 3 specific evidence-backed signals.")

class FinalSnapshot(BaseModel):
    submission_id: str = Field(description="The unique ID.")
    phase: str = "final_snapshot"
    positioning_core: CorePositioning
    positioning_tier: PositioningTier
    blind_spots: List[BlindSpot]
    competitive_advantage: List[str]
    evolution_path: List[EvolutionAction]

parser = PydanticOutputParser(pydantic_object=FinalSnapshot)

# 3. The Prompt (Updated to support nested logic)
snapshot_prompt = ChatPromptTemplate.from_template(
    """
    SYSTEM: You are the Lead Auditor for Global Legal Rankings. 
    Your mission is to transform the current SUBMISSION into an 'Elite' tier entry.
    
    STRICT GROUNDING RULE: 
    Every insight must be a direct extraction from the provided Submission. 
    If a name, matter, or specific friction point is not in the {raw_text} or {history}, DO NOT invent it.

    CONTEXT:
    - Current Submission Data: {raw_text}
    - Interrogation Evidence: {history}
    - Practice Model: {practice_model}
    - gaps identified: {gaps}

    INSTRUCTIONS:
    1. **Submission Blind Spots (Exactly 4)**: Identify high-stakes gaps in the current evidence. 
       - Focus on: "Partner concentration in [Name]", "Missing proof of leadership in [Case X]", or "Lack of value-at-stake metrics".
    2. **Submission Advantages (Exactly 2)**: Isolate the 'Elite' signals already present.
       - Focus on: Unique regulatory authorizations or high-friction outcomes found in the text.
    3. **Elite Evolution Path (Exactly 5 Steps)**: Practical, technical steps to upgrade THIS specific submission.
       - Actions must be operational (e.g., "Quantify the financial impact of the [Matter Name] restructure").

    OUTPUT STYLE: 
    Technical, objective, and evidence-backed. Use the names of partners and cases found in the submission.

    {format_instructions}
    """
)

llm = get_llm(temperature=0.2)
snapshot_chain = (
    snapshot_prompt.partial(format_instructions=parser.get_format_instructions())
    | llm
    | parser
)