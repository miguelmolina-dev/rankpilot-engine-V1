from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
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
    You are a Senior Legal Directory Researcher for Chambers & Partners. 
    Analyze the following legal submission text and extract the core positioning data.
    
    TEXT FROM SUBMISSION:
    {text}
    
    INSTRUCTIONS:
    - Identify the unique 'Practice Model' (e.g., instead of just 'Banking', use 'Regulatory-Heavy FinTech').
    - Find 3 clear signals of complexity or prestige.
    - Identify what is missing for a Top-Tier ranking.
    
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