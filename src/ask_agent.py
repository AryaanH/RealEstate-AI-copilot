import os
import json
import requests
from dotenv import load_dotenv

# Load env from config/.env
load_dotenv(dotenv_path=os.path.join("config", ".env"))

AGENT_ENDPOINT = os.getenv("AGENT_ENDPOINT", "").strip()
API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "").strip()

if not AGENT_ENDPOINT or not API_KEY:
    raise RuntimeError(
        "Missing AGENT_ENDPOINT or AZURE_OPENAI_API_KEY in config/.env")

HEADERS = {
    "Content-Type": "application/json",
    "api-key": API_KEY
}


def ask_agent(question: str) -> str:
    """
    Sends a user question to Azure AI Foundry Agent (which already has Knowledge/Vector Store attached).
    The prompt tells the agent to ONLY use the uploaded documents.
    """
    payload = {
        "messages": [
            {
                "role": "user",
                "content": (
                    "Use ONLY the connected knowledge base (uploaded PDFs) to answer. "
                    "If the information is not in knowledge, reply exactly: 'Not in knowledge.'\n\n"
                    f"Question: {question}"
                )
            }
        ]
    }

    r = requests.post(AGENT_ENDPOINT, headers=HEADERS,
                      data=json.dumps(payload), timeout=60)
    r.raise_for_status()
    data = r.json()

    # Typical Agent Responses shape:
    # {"output":{"message":{"content":[{"type":"text","text":"..."}]}}}
    out = data.get("output", {}).get("message", {}).get("content", [])
    texts = []
    for part in out:
        if isinstance(part, dict) and part.get("type") == "text":
            texts.append(part.get("text", ""))
    return "\n".join(texts).strip() or json.dumps(data, indent=2)


def cli():
    print("AURA — Real-Estate AI (Agent-connected). Type 'exit' to quit.")
    while True:
        q = input("\nYour question: ").strip()
        if q.lower() == "exit":
            break
        try:
            print("Thinking…")
            ans = ask_agent(q)
            print("\nAURA:", ans)
        except requests.HTTPError as e:
            print("\nHTTP Error:", e.response.status_code, e.response.text)
        except Exception as e:
            print("\nError:", str(e))


if __name__ == "__main__":
    cli()
