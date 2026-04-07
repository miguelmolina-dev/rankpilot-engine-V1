import requests
import json
import time

SERVER_URL = "http://127.0.0.1:8000/process"

def print_json(data):
    print(json.dumps(data, indent=2))

def run_simulation():
    # Initial State matching the RankPilotState TypedDict
    state = {
        "submission_id": "test_submission_123",
        "metadata": {
            "file_path": "test.txt",
            "directory": None,
            "current_band": None,
            "target_band": None
        },
        "raw_text": "Our law firm specializes in corporate M&A and has completed 50 deals this year.",
        "new_answer": {
            "question_text": "",
            "answer": ""
        },
        "history": [],
        "current_step": 0,
        "gaps": [],
        "positioning_core": {
            "practice_model": "",
            "practice_definition": "",
            "confidence_score": 0.0,
            "signals": []
        },
        "positioning_tier": {
            "label": "",
            "explanation": ""
        },
        "blind_spots": [],
        "competitive_advantage": [],
        "evolution_path": [],
        "next_node": "analyze_structure"
    }

    print("--- Starting Simulation ---")

    while True:
        print(f"\nSending state to server... (next_node: {state.get('next_node')})")
        response = requests.post(SERVER_URL, json=state)

        if response.status_code != 200:
            print(f"Error: Server returned status {response.status_code}")
            print(response.text)
            break

        result = response.json()
        print("Server returned update:")
        print_json(result)

        # Merge result into state (simulating Laravel keeping state)
        for key, value in result.items():
            state[key] = value

        # Ensure that if the backend omits any fields, they exist in our next payload
        # (Since the API requires the full RankPilotState schema)
        if "positioning_tier" in state and isinstance(state["positioning_tier"], dict) and "explanation" not in state["positioning_tier"]:
            state["positioning_tier"]["explanation"] = "Default explanation"

        if "positioning_core" in state and isinstance(state["positioning_core"], dict):
            for k in ["practice_model", "practice_definition", "signals"]:
                if k not in state["positioning_core"]:
                    state["positioning_core"][k] = "" if k != "signals" else []
            if "confidence_score" not in state["positioning_core"]:
                state["positioning_core"]["confidence_score"] = 0.0

        if state.get("next_node") == "generate_snapshot" and "blind_spots" in state and len(state["blind_spots"]) > 0:
             # Reached end
             print("\n--- Simulation Complete ---")
             print("Final State:")
             print_json(state)
             break

        if state.get("next_node") is None or "generate_snapshot" not in state.get("next_node", ""):
             # Just safety loop break if we reach a steady state without advancing to snapshot
             if state.get("current_step", 0) > 10:
                 print("\n--- Ending Simulation (Step Limit Reached) ---")
                 break
        elif state.get("next_node") == "generate_snapshot" and len(state.get("blind_spots", [])) == 0:
             # Try one more post to let generate_snapshot run
             print("\nSending state to server... (next_node: generate_snapshot)")
             response = requests.post(SERVER_URL, json=state)
             if response.status_code == 200:
                 result = response.json()
                 print("Server returned update:")
                 print_json(result)
                 for key, value in result.items():
                     state[key] = value
             print("\n--- Simulation Complete ---")
             print("Final State:")
             print_json(state)
             break

        # Delay to avoid hammering
        time.sleep(1)

if __name__ == "__main__":
    run_simulation()
