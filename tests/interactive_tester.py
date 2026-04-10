import sys
import httpx
import json
import argparse
from send_base64_file import send_file

def run_interactive_session(filepath, url="http://localhost:8001/process"):
    print("=== Starting Interactive Test Session ===")

    # 1. Send the initial file
    state = send_file(filepath, url)

    if not state:
        print("Failed to start session.")
        return

    while True:
        # Check if we are in the interrogation step and need an answer
        if state.get("next_node") == "interrogate" and state.get("new_answer") and state["new_answer"].get("question_text"):
            question = state["new_answer"]["question_text"]
            print("\n" + "="*50)
            print(f"Server Question: {question}")
            print("="*50)

            # 2. Get user input
            answer = input("\nYour Answer (type 'exit' to quit): ")

            if answer.lower() == 'exit':
                print("Exiting interactive session.")
                break

            # 3. Update state with the answer
            state["new_answer"]["answer"] = answer

            # Send back the updated state
            print(f"\nSending answer back to {url}...")
            try:
                with httpx.Client(timeout=500.0) as client:
                    response = client.post(url, json=state)

                print(f"Status Code: {response.status_code}")
                state = response.json()
            except Exception as e:
                print(f"Error communicating with server: {e}")
                break

        # Check if the workflow is complete
        elif state.get("next_node") == "generate_snapshot" or state.get("status") == "completed" or not state.get("next_node"):
             print("\n=== Workflow Completed or Transitioned out of Interrogation ===")
             print("Final State Snippet:")
             # Print a summary to avoid huge output
             summary = {
                 "current_step": state.get("current_step"),
                 "next_node": state.get("next_node"),
                 "blind_spots_count": len(state.get("blind_spots", [])),
                 "evolution_path_count": len(state.get("evolution_path", [])),
                 "has_executive_summary": bool(state.get("executive_summary"))
             }
             print(json.dumps(summary, indent=2))
             break
        else:
             print("\nUnexpected state received:")
             print(json.dumps({k: v for k, v in state.items() if k in ['current_step', 'next_node', 'status']}, indent=2))
             break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run an interactive session with the LangGraph backend.")
    parser.add_argument("filepath", help="Path to the initial file to process")
    parser.add_argument("--url", default="http://localhost:8001/process", help="URL of the process endpoint")

    args = parser.parse_args()

    # We need to handle KeyboardInterrupt gracefully
    try:
        run_interactive_session(args.filepath, args.url)
    except KeyboardInterrupt:
        print("\nSession interrupted by user.")
