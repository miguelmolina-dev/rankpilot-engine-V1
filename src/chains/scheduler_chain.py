from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm_manager import get_llm # Using your existing manager
from langchain_core.output_parsers import PydanticOutputParser

# 1. Define the Schema for the Output (The Roadmap)
class MilestoneSchema(BaseModel):
    category: str = Field(description="Category: Narrative Strategy, Quantitative Density, Leadership Balance, or Volume Expansion")
    action_title: str = Field(description="A 5-8 word technical headline for the milestone")
    why_it_matters: str = Field(description="Strategic justification for Tier/Band elevation based on ranking criteria")
    technical_instruction: str = Field(description="Step-by-step 'How-to' for the associate lawyer to execute")
    priority_level: int = Field(description="Integer from 1 (Critical) to 5 (Standard)")
    days_before_deadline: int = Field(description="Calculated target days before the submission date")

class SchedulerResponse(BaseModel):
    evolution_path: List[MilestoneSchema] = Field(description="A list of exactly 5 strategic milestones")

# 1. Initialize the Parser
parser = PydanticOutputParser(pydantic_object=SchedulerResponse)

# 2. Create the Strategic Prompt
# We use a cold, project-manager persona for the scheduler
STRATEGIC_SCHEDULER_PROMPT = ChatPromptTemplate.from_template(
    """
    SYSTEM: 
    You are the "Lead Architect & Project Manager" for International Legal Rankings. 
    Your mission is to engineer a 5-step strategic roadmap that guarantees a Band 1/Tier 1 evaluation.
    
    OPERATIONAL CONTEXT:
    - Deadline: {submission_deadline}
    - Location/Area: {location} / {practice_area}
    - Found Gaps: {gaps}
    - Blind Spots: {blind_spots}
    - Evidence: {raw_text}

    CHAIN-OF-THOUGHT INSTRUCTIONS:
    1. ANALYZE TEMPORAL URGENCY: Calculate the remaining window. High urgency (<30 days) requires "triage" actions. Low urgency (>60 days) allows for "structural" growth.
    2. CONTENT VOLUME CHECK: If the matter count is below 20, Step 1 and 2 MUST prioritize "Content Discovery" to reach the maximum limit allowed by Chambers/Legal 500.
    3. STRATEGIC POSITIONING: Identify the "Market Leader" signal for {practice_area}. Ensure milestones address how to pivot the narrative from "Service Provider" to "Industry Authority."
    4. SEQUENCING: Order steps from "Heavy Lifting" (Gathering data) to "Surgical Refinement" (Polishing text).

    OUTPUT REQUIREMENTS (5 Milestones):
    For each milestone, you MUST provide:
    - CATEGORY: [Strategic Narrative, Quantitative Density, Leadership Balance, or Volume Expansion].
    - ACTION TITLE: A technical, professional headline.
    - WHY IT MATTERS: Explain the "Tier Elevation" logic (e.g., "Researchers prioritize [X] when deciding between Band 2 and Band 1").
    - TECHNICAL INSTRUCTION: A specific "How-to" for the Associate Lawyer.
    - DAYS BEFORE DEADLINE: The integer indicating when this must be completed.
    - PRIORITY: 1 (Critical) to 5 (Standard).

    STYLE: 
    Cold, analytical, and authoritative. Use the names of partners and cases found in {raw_text}. Do not use generic advice; be hyper-specific to this submission.
    {format_instructions}
    """
)

# 3. Initialize LLM (Low temperature for precise logic)
llm = get_llm(temperature=0.1) 

# 4. Build the Chain with Structured Output
scheduler_chain = (
    STRATEGIC_SCHEDULER_PROMPT.partial(format_instructions=parser.get_format_instructions()) 
    | llm 
    | parser
)