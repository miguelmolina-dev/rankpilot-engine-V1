from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm_manager import get_llm
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

# 1. Define the Schema for the Question
class InterrogationQuestion(BaseModel):
    id: str = Field(description="Unique ID for the question, e.g., q_client_03")
    text: str = Field(description="The strategic question for the lawyer.")

# 2. Set up the Parser
parser = PydanticOutputParser(pydantic_object=InterrogationQuestion)

# 3. Create the Strategic Prompt
# Notice the "Persona" - we want a cold, professional researcher.
question_prompt = ChatPromptTemplate.from_template(
    """
    SYSTEM: You are a Senior Legal Auditor for Global Rankings. 
    Your mission: Transform a 'Consolidated' submission into an 'Elite' one by extracting high-friction evidence, leadership evidence in the matters and ways to improve the submission.
    
    CONTEXT:
    - Current Gaps: {gaps}
    - History: {history}
    - last user answer: {last_answer}
    
    INSTRUCTIONS:
    1. **Elite Micro-Validation**: Begin by acknowledging the last user response. 
       - RULE: Maximum 15 words. 
       - TONE: Professional, coaching, and analytical. 
       - EXAMPLE: "Strong evidence of regulatory friction. Let's isolate the specific C-suite impact."

    2. **The Surgical Question**: Ask EXACTLY ONE question to bridge a remaining gap. (cite the case name, the specific friction point, or the exact leadership claim you want to validate.)
       - RULE: No "And", "Also", or multiple sentences. 
       - RULE: Maximum 40 words.
       - FOCUS: Target the 'Why' and 'How' of complexity (Friction).

    3. **No Preamble**: Do not use pleasantries like "Hello", "Interesting", or "Thank you". 

    4. **Drill Down**: If the history shows a vague answer, the question MUST demand a specific name, value, or legal hurdle.

    {format_instructions}
    """
)

# 4. Initialize LLM (GPT-4o)
llm = get_llm(temperature=0.7) # Slightly higher temperature for more varied questioning

# 5. Build the Chain
question_chain = (
    question_prompt.partial(format_instructions=parser.get_format_instructions())
    | llm
    | parser
)