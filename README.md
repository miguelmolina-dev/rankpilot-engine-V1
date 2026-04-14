# RankPilot Engine

RankPilot Engine is a FastAPI backend application leveraging LangGraph and LangChain to orchestrate LLM-driven document processing workflows. It analyzes legal submissions (e.g., Chambers, Legal 500) provided in PDF or DOCX format, conducts an interactive structural analysis and interrogation loop, and generates actionable strategic roadmaps and an executive summary.

The backend communicates with a Laravel application (or other clients) primarily via the `/process` API endpoint.

## API Specifications

### `POST /process`

This endpoint triggers or resumes the LangGraph workflow. It operates statelessly: it does not persist the state itself. Instead, it expects the entire state to be passed in the request body and returns the updated state after each workflow step. The client is responsible for persisting this state and sending it back in subsequent requests.

The payload represents the `RankPilotState` defined in `src/graph/state.py`.

**Note on Files:** The system expects the document content to be passed as a base64-encoded string within the `metadata.file_base64` property on the initial request.

---

### 1. The First Input

This is the initial payload sent to the system to begin processing a document. Only the `submission_id` and the `metadata.file_base64` are strictly required to start the process.

**JSON Payload Example (First Input):**
```json
{
  "submission_id": "sub_12345",
  "metadata": {
    "file_base64": "JVBERi0xLjMKJcTl8uXrp/Og0MTGCjQgMCBvYmoKPDwgL0xlbmd0aCA1IDAgUiAvRmlsdGVyIC9GbGF0ZURlY29kZSA...",
    "region": "Latin America",
    "practice_area": "Tax",
    "location": "São Paulo",
    "firm_name": ""
  }
}
```

---

### 2. The First Output

After the initial request, the structural analyzer parses the base64 document, extracts the raw text (stored in `raw_text`), analyzes it, identifies initial gaps, updates the `positioning_core`, and prepares the first interrogation question. The state is then returned to the client to wait for an answer.

**JSON Payload Example (First Output):**
```json
{
  "submission_id": "sub_12345",
  "metadata": {
    "file_base64": "JVBERi0xLjMKJcTl8uXrp/Og0MTGCjQgMCBvYmoKPDwgL0xlbmd0aCA1IDAgUiAvRmlsdGVyIC9GbGF0ZURlY29kZSA...",
    "region": "Latin America",
    "practice_area": "Tax",
    "location": "São Paulo",
    "firm_name": "Example Law Firm LLC",
    "directory": null,
    "current_band": null,
    "target_band": null,
    "submission_deadline": null
  },
  "raw_text": "Extracted text content from the document...",
  "current_step": 1,
  "next_node": "interrogate",
  "gaps": [
    "Lack of quantitative evidence in significant matters.",
    "Unclear differentiation from main competitors."
  ],
  "positioning_core": {
    "practice_model": "Full-Service",
    "practice_definition": "Comprehensive tax advisory and litigation.",
    "confidence_score": 0.85,
    "signals": ["Cross-border transactions", "High-profile litigation"]
  },
  "history": [],
  "new_answer": {
    "question_text": "Could you provide more specific figures or deal values for the cross-border transactions mentioned?",
    "answer": ""
  },
  "positioning_tier": null,
  "blind_spots": [],
  "competitive_advantage": [],
  "evolution_path": [],
  "executive_summary": null
}
```

---

### 3. Input During the Interrogation Loop

To resume the workflow, the client sends back the state it received from the previous output, but with the user's response populated in the `new_answer.answer` field. The state will be routed directly to the `interrogate` node.

**JSON Payload Example (Input During Loop):**
```json
{
  "submission_id": "sub_12345",
  "metadata": {
    "file_base64": "JVBERi0xLjMKJcTl8uXrp/Og0MTGCjQgMCBvYmoKPDwgL0xlbmd0aCA1IDAgUiAvRmlsdGVyIC9GbGF0ZURlY29kZSA...",
    "region": "Latin America",
    "practice_area": "Tax",
    "location": "São Paulo",
    "firm_name": "Example Law Firm LLC"
  },
  "raw_text": "Extracted text content from the document...",
  "current_step": 1,
  "next_node": "interrogate",
  "gaps": [
    "Lack of quantitative evidence in significant matters.",
    "Unclear differentiation from main competitors."
  ],
  "positioning_core": {
    "practice_model": "Full-Service",
    "practice_definition": "Comprehensive tax advisory and litigation.",
    "confidence_score": 0.85,
    "signals": ["Cross-border transactions", "High-profile litigation"]
  },
  "history": [],
  "new_answer": {
    "question_text": "Could you provide more specific figures or deal values for the cross-border transactions mentioned?",
    "answer": "Yes, we handled over $500M in cross-border tax restructuring last year."
  }
}
```

---

### 4. Output During the Interrogation Loop

The interrogator processes the user's answer, appends the Q&A to the `history`, increments the `current_step`, and typically generates a new question if the interrogation is not yet complete (until `current_step >= 6`).

**JSON Payload Example (Output During Loop):**
```json
{
  "submission_id": "sub_12345",
  "metadata": {
    "file_base64": "JVBERi0xLjMKJcTl8uXrp/Og0MTGCjQgMCBvYmoKPDwgL0xlbmd0aCA1IDAgUiAvRmlsdGVyIC9GbGF0ZURlY29kZSA...",
    "region": "Latin America",
    "practice_area": "Tax",
    "location": "São Paulo",
    "firm_name": "Example Law Firm LLC"
  },
  "raw_text": "Extracted text content from the document...",
  "current_step": 2,
  "next_node": "interrogate",
  "gaps": [
    "Lack of quantitative evidence in significant matters.",
    "Unclear differentiation from main competitors."
  ],
  "positioning_core": {
    "practice_model": "Full-Service",
    "practice_definition": "Comprehensive tax advisory and litigation.",
    "confidence_score": 0.85,
    "signals": ["Cross-border transactions", "High-profile litigation"]
  },
  "history": [
    "Q_Text: Could you provide more specific figures or deal values for the cross-border transactions mentioned? | Answer: Yes, we handled over $500M in cross-border tax restructuring last year."
  ],
  "new_answer": {
    "question_text": "How does your team's approach to tax restructuring differentiate from your primary competitors?",
    "answer": ""
  }
}
```

---

### 5. Final Output

Once the interrogation phase completes (`current_step >= 6`), the workflow proceeds to generate the snapshot, strategic schedule, and executive summary. The final output is returned with `next_node` empty or pointing to `END`, and the final results populated.

**JSON Payload Example (Final Output):**
```json
{
  "submission_id": "sub_12345",
  "metadata": {
    "file_base64": "JVBERi0xLjMKJcTl8uXrp/Og0MTGCjQgMCBvYmoKPDwgL0xlbmd0aCA1IDAgUiAvRmlsdGVyIC9GbGF0ZURlY29kZSA...",
    "region": "Latin America",
    "practice_area": "Tax",
    "location": "São Paulo",
    "firm_name": "Example Law Firm LLC"
  },
  "raw_text": "Extracted text content from the document...",
  "current_step": 6,
  "next_node": "",
  "gaps": [
    "Lack of quantitative evidence in significant matters.",
    "Unclear differentiation from main competitors."
  ],
  "positioning_core": {
    "practice_model": "Full-Service",
    "practice_definition": "Comprehensive tax advisory and litigation.",
    "confidence_score": 0.85,
    "signals": ["Cross-border transactions", "High-profile litigation"]
  },
  "positioning_tier": {
    "label": "Tier 1 Contender",
    "explanation": "Strong financials and key matters, but lacks some narrative differentiation."
  },
  "history": [
    "Q_Text: Could you provide more specific figures... | Answer: Yes, we handled over $500M...",
    "...(more history)..."
  ],
  "new_answer": {
    "question_text": "Final question...",
    "answer": "Final answer..."
  },
  "blind_spots": [
    {
      "issue": "Overreliance on Partner X",
      "description": "Matter descriptions lean heavily on the senior partner, masking associate contributions."
    }
  ],
  "competitive_advantage": [
    "Unmatched volume of cross-border tax restructuring deals.",
    "Proprietary legal tech used for risk assessment."
  ],
  "evolution_path": [
    {
      "category": "Quantitative Density",
      "action_title": "Inject Deal Values",
      "why_it_matters": "Demonstrates market share and financial impact.",
      "technical_instruction": "Add precise $ values or % growth to the top 5 matters.",
      "priority_level": 1,
      "days_before_deadline": 14
    }
  ],
  "executive_summary": {
    "overall_score": 78,
    "risk_level": "Moderate",
    "strategic_verdict": "The submission highlights strong deals but fails to clearly distinguish the firm's unique methodology. Adding deal values and associate profiles will strengthen the bid.",
    "top_differentiators": ["Cross-border deal volume", "Tech integration"],
    "audit_letter_markdown": "# Audit Letter\n\nDear Partner,\n\nWe have reviewed your submission..."
  }
}
```
