from src.graph.state import RankPilotState
from src.chains.question_chain import question_chain

from src.graph.state import NewAnswer

def interrogator_node(state: RankPilotState):
    print("--- [NODE] Starting Interrogation Step ---")
    
    # 1. Ingestion: Accessing the dictionary safely
    # RankPilotState is now a BaseModel
    new_ans = state.new_answer
    history = state.history or []
    current_step = state.current_step

    print(f"Current Step: {current_step}")

    # 2. Update History with the previous interaction
    if new_ans and new_ans.answer:
        q_text = new_ans.question_text or 'Unknown Question'
        answer = new_ans.answer
        history.append(f"Q: {q_text} | A: {answer}")

    # 3. Check for Completion (Threshold: 6 steps)
    if current_step >= 6:
        print("--- [NODE] Interrogation Complete. Transitioning to Snapshot ---")
        return {
            "history": history,
            "next_node": "generate_snapshot", # Triggers the next phase
            "current_step": current_step + 1
        }

    # 4. Processing: Fix the 'raw_text' mapping
    # Your state uses 'raw_text', NOT 'file_content'
    raw_text = state.raw_text
    
    input_data = {
        "raw_text": raw_text,
        "history": history,
        "current_step": current_step,
        "gaps": state.gaps or "No specific gaps identified yet.",
        "last_answer": new_ans.answer if new_ans else "First question - No previous answer."
    }
    
    # 5. Output: Generate the next Tyler Durden question
    try:
        response = question_chain.invoke(input_data)
        # Note: If using a custom chain, ensure it returns an object with a .text attribute
        next_question = response.text if hasattr(response, 'text') else str(response)
        
        print(f"Next Question: {next_question}")

        return {
            "history": history,
            "current_step": current_step + 1,
            "new_answer": NewAnswer(
                question_text=next_question,
                answer="" # Laravel will fill this in the next hit
            ),
            "next_node": "interrogate" 
        }
    except Exception as e:
        print(f"Error in interrogator Chain: {e}")
        raise e
