from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
from src.utils.llm_manager import get_llm

# 1. Define the Schema for the Output
class ExtractionResult(BaseModel):
    practice_model: str = Field(description="Short name for the practice type (e.g., 'Distress-Linked Finance')")
    definition: str = Field(description="One-sentence technical definition of this model.")
    confidence_score: float = Field(description="Score between 0.0 and 1.0 based on the initial PDF richness.")
    initial_signals: List[str] = Field(description="Exactly 3 specific strengths or 'proof points' found in the text.")
    gaps: List[str] = Field(description="A list of 4 - 6 gaps identified in the document structure.")
    firm_name: str = Field(description="The name of the law firm as mentioned in the submission.")

# 2. Set up the Parser
parser = PydanticOutputParser(pydantic_object=ExtractionResult)

# 3. Create the Prompt
extraction_prompt = ChatPromptTemplate.from_template(
    """
    ### ROLE
    You are an Elite Legal Strategy Consultant and Lead Researcher for Chambers & Partners. You possess a "market-microscope" ability to distinguish between generic legal work and Top-Tier (Band 1) sophistication.

    ### CONTEXT
    The following text is a legal directory submission. Your goal is to dissect this text to find the firm's competitive edge and, more importantly, identify the "credibility deficit" preventing them from absolute market dominance.

    ### EXTRACTION TASK
    Analyze the [SUBMISSION TEXT] and extract data based on these specific criteria:

    1. **Practice Model**: Do not use generic labels (e.g., "Corporate"). Instead, identify the specific "Hybrid Niche" or "Market Focus" presented (e.g., "Cross-Border Tech M&A for Emerging Markets").
    2. **Definition**: Write a high-level, one-sentence technical definition that describes the firm’s unique methodology or sector-specific specialization.
    3. **Initial Signals (Exactly 3)**: Extract evidence of "Market Gravity." Look for:
        - High-stakes value (USD amounts).
        - Novelty (First-of-its-kind litigation or regulatory firsts).
        - Multi-jurisdictional complexity.
    4. **Gaps (4-6 Items)**: Be ruthless. Identify what is missing based on Chambers' "Band 1" standards:
        - Lack of client feedback snippets? 
        - Absence of market-leading individual rankings?
        - Insufficient geographical breadth? 
        - Weakness in "Bet-the-Company" case studies?
    5. **Firm Name**: Exact legal entity name as it appears.

    ### CONSTRAINTS
    - If the text is insufficient, provide a lower `confidence_score`.
    - Every "Gap" must be a structural weakness of the *submission*, not a general legal industry problem.
    - Professional, objective, and analytical tone.

    ### SUBMISSION TEXT:
    {text}

    {format_instructions}
    """
)

# 4. Initialize the Model (Gemini)
# Ensure your GOOGLE_API_KEY is in your .env
llm = get_llm(temperature=0)

# 5. Build the Chain using LCEL (LangChain Expression Language)
extraction_chain = (
    extraction_prompt.partial(format_instructions=parser.get_format_instructions()) 
    | llm 
    | parser
)