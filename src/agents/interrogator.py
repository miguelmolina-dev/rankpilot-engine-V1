from src.graph.state import RankPilotState
from src.chains.question_chain import question_chain

def interrogator_node(state: RankPilotState):
    print("--- [NODE] Starting Interrogation Step ---")
    # 1. Ingestion: Process incoming Laravel JSON
    # Use .get() to avoid KeyError if Laravel sends a different structure
    new_ans = state.get("new_answer", {})
    history = state.get("history", [])

    print(f"Current Step before increment: {state.get('current_step', 0)}")

    if new_ans:
        q_text = new_ans.get('question_text', 'Unknown Question')
        answer = new_ans.get('answer', '')
        history.append(f"Q_Text: {q_text} | Answer: {answer}")

    # 2. Check for Completion (Transition to Snapshot)
    if state.get("current_step", 0) >= 3:
        print("--- [NODE] Interrogation Complete. Moving to Snapshot Generation ---")
        return {
            "submission_id": state.get("submission_id"),
            "status": "completed", # Ensure your router recognizes 'completed'
            "current_step": state.get("current_step", 0) + 1,
            "next_node": "generate_snapshot", 
            "history": history
        }

    # 3. Processing: Use 'text' from ingestion to avoid KeyError
    # Laravel Initial JSON provides text inside 'file_content'
    raw_text = state.get("file_content", {}).get("text", "")
    
    input_data = {
        "raw_text": raw_text,
        "history": history,
        "current_step": state.get("current_step", 0),
        "gaps": state.get("gaps", "No specific gaps identified yet."),
        "last_answer": state.get("new_answer", "this is the first question, no answer yet.")
    }
    
    # 4. Output: Call chain and handle Pydantic object correctly
    response = question_chain.invoke(input_data)
    print("--- [DEBUG] EXITING INTERROGATOR NODE. ---")
    print(f"next_question: {response.text}")
    return {
        "submission_id": state.get("submission_id"),
        "status": "continue",
        "current_step": state.get("current_step", 0) + 1,
        "history": history,
        "new_answer": {
            "question_text": response.text,
            "answer": "" # We will fill this in the next hit from Laravel
        },
        "next_node": "interrogate" 
    }