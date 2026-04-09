from src.graph.state import RankPilotState
from src.chains.question_chain import question_chain

def interrogator_node(state: RankPilotState):
    print("--- [NODE] Starting Interrogation Step ---")
    # 1. Ingestion: Process incoming Laravel JSON
    new_ans = state.new_answer
    history = state.history

    print(f"Current Step before increment: {state.current_step}")

    if new_ans:
        q_text = new_ans.question_text if new_ans.question_text else 'Unknown Question'
        answer = new_ans.answer if new_ans.answer else ''
        history.append(f"Q_Text: {q_text} | Answer: {answer}")

    # 2. Check for Completion (Transition to Snapshot)
    if state.current_step >= 3:
        print("--- [NODE] Interrogation Complete. Moving to Snapshot Generation ---")
        return {
            "submission_id": state.submission_id,
            "status": "completed", # Ensure your router recognizes 'completed'
            "current_step": state.current_step + 1,
            "next_node": "generate_snapshot", 
            "history": history
        }

    # 3. Processing: Extract text from state to pass to LLM
    raw_text = state.raw_text if state.raw_text else ""
    
    input_data = {
        "raw_text": raw_text,
        "history": history,
        "current_step": state.current_step,
        "gaps": state.gaps if state.gaps else "No specific gaps identified yet.",
        "last_answer": state.new_answer if state.new_answer else "this is the first question, no answer yet."
    }
    
    # 4. Output: Call chain and handle Pydantic object correctly
    response = question_chain.invoke(input_data)
    print("--- [DEBUG] EXITING INTERROGATOR NODE. ---")
    print(f"next_question: {response.text}")
    return {
        "submission_id": state.submission_id,
        "status": "continue",
        "current_step": state.current_step + 1,
        "history": history,
        "new_answer": {
            "question_text": response.text,
            "answer": "" # We will fill this in the next hit from Laravel
        },
        "next_node": "interrogate" 
    }