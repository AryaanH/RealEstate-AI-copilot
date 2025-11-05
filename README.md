# Ask any suburb’s median price, rental yield, or council zoning in 3 seconds — powered by Azure AI Studio + 15 official ABS/Domain PDFs

Python client that talks to **Azure AI Foundry Agent** (with Knowledge / Vector Store of AU real-estate PDFs).
It returns **source-aware** answers using only the uploaded documents (RAG).

## How it works
- Azure AI Foundry **Agent** hosts the model + vector store (indexed PDFs).
- This script calls the **Agent API endpoint** (not the base model endpoint).
- Guardrail: if info isn’t in the PDFs, it replies **“Not in knowledge.”**

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp config/.env.example config/.env
# fill AGENT_ENDPOINT + AZURE_OPENAI_API_KEY in config/.env
python src/ask_agent.py
