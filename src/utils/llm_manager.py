import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm(temperature=0):
    """
    Returns a LangChain LLM instance based on the .env configuration.
    Supports OpenRouter for local dev and Direct OpenAI for production.
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "openrouter":
        return ChatOpenAI(
            model=os.getenv("OPENROUTER_MODEL"),
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=temperature,
            default_headers={
                "HTTP-Referer": "http://localhost:3000", # Required by OpenRouter
                "X-Title": "RankPilot_Dev"
            }
        )
    
    # Default to Direct OpenAI (Production)
    return ChatOpenAI(
        model="gpt-5.4-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=temperature
    )