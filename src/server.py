from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from typing import Optional, List

app = FastAPI(
    title="AURA — Real-Estate AI Copilot API",
    version="1.0.0"
)

#Azure AI Foundry client setup
project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint="https://real-estate-ai-resource.services.ai.azure.com/api/projects/real-estate-ai"
)

AGENT_ID = "asst_mNSYbCoZ58f61IbiWlb0JVou"
agent = project.agents.get_agent(AGENT_ID)


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None  # if frontend wants to keep a session


class ChatResponse(BaseModel):
    reply: str
    thread_id: str


#Helper to read latest aAI message
def get_latest_assistant_message(thread_id: str) -> str:
    msgs = list(project.agents.messages.list(thread_id=thread_id))

    assistant_msgs = []
    for m in msgs:
        if m.role != "assistant" or not m.content:
            continue
        for part in m.content:
            text_obj = getattr(part, "text", None)
            if text_obj and getattr(text_obj, "value", None):
                assistant_msgs.append((getattr(m, "created_at", 0), text_obj.value))

    if not assistant_msgs:
        return "(no response)"

    assistant_msgs.sort(key=lambda x: x[0])
    return assistant_msgs[-1][1].strip()


#Routes

@app.get("/")
def root():
    return {"status": "ok", "message": "AURA API is running"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # 1) Ensure message exists
    user_msg = (req.message or "").strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Empty message")

    # 2) Use existing thread_id or create a new thread
    if req.thread_id:
        thread_id = req.thread_id
    else:
        thread = project.agents.threads.create()
        thread_id = thread.id

    # 3) Create user message in that thread
    project.agents.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_msg
    )

    # 4) Run the agent
    run = project.agents.runs.create_and_process(
        thread_id=thread_id,
        agent_id=AGENT_ID
    )

    if run.status == "failed":
        # You can inspect run.last_error here if needed
        raise HTTPException(status_code=500, detail="Agent run failed")

    # 5) Get the latest assistant reply
    reply_text = get_latest_assistant_message(thread_id)

    return ChatResponse(
        reply=reply_text,
        thread_id=thread_id
    )