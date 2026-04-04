from typing import Dict, Any
from src.graph.state import RankPilotState
from src.chains.executive_writer_chain import executive_writer_chain

def executive_writer_node(state: RankPilotState) -> Dict[str, Any]:
    """
    Executive Writer Agent:
    Synthesizes all technical and strategic data into a high-authority 
    report and a formal Audit Letter.
    """
    print("--- [NODE] Finalizing Executive Synthesis ---")

    # 1. Gather all inputs from the Parallel Nodes
    # positioning_core comes from the Snapshot Generator
    pos_core = state.get("positioning_core", {})
    
    # evolution_path comes from the Strategic Scheduler
    evolution_path = state.get("evolution_path", [])
    formatted_path = "\n".join([
        f"STEP {i+1}: {step['action_title']} ({step['category']})\n"
        f"WHY: {step['why_it_matters']}\n"
        f"HOW: {step['technical_instruction']}\n"
        for i, step in enumerate(evolution_path)
    ]) if evolution_path else "No roadmap generated."
    
    # metadata includes the firm_name we extracted earlier
    metadata = state.get("metadata", {})
    
    # 2. Prepare the Payload for the Writer Chain
    # We combine every signal, gap, and strategy into one context
    input_data = {
        "firm_name": metadata.get("firm_name", "the Firm"),
        "practice_area": metadata.get("practice_area", "General Law"),
        "region": metadata.get("region", "Global"),
        "positioning_tier": state.get("positioning_tier", {}),
        "competitive_advantage": state.get("competitive_advantage", []),
        "gaps": state.get("gaps", []),
        "blind_spots": state.get("blind_spots", []),
        "evolution_path": formatted_path,
        "positioning_core": pos_core,
        "history": state.get("history", [])
    }
    try:
        # 3. Invoke the Synthesis Chain
        # This chain uses a higher temperature (0.7) for sophisticated prose
        response = executive_writer_chain.invoke(input_data)
        
        print(f"--- [DEBUG] Synthesis Complete. Overall Score: {response.overall_score} ---")

        # 4. Final State Update
        return {
            "executive_summary": {
                "overall_score": response.overall_score,
                "risk_level": response.risk_level,
                "strategic_verdict": response.strategic_verdict,
                "top_differentiators": state.get("competitive_advantage", []),
                "audit_letter_markdown": response.audit_letter_markdown
            },
            "current_step": state.get("current_step", 0) + 1
        }
    except Exception as e:
        print(f"--- [ERROR] Executive Writer Node Failed: {str(e)} ---")
        return {
            "executive_summary": {
                "overall_score": 0,
                "risk_level": "Critical",
                "strategic_verdict": "Synthesis Failed. No actionable insights generated.",
                "top_differentiators": [],
                "audit_letter_markdown": "An error occurred during synthesis. Please review the logs."
            },
            "current_step": state.get("current_step", 0) + 1
        }