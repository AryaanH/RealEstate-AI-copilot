import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# ---- CONFIG ----
PROJECT_ENDPOINT = os.getenv(
    "PROJECT_ENDPOINT",
    "https://real-estate-ai-resource.services.ai.azure.com/api/projects/real-estate-ai"
)
AGENT_ID = os.getenv("AGENT_ID", "asst_Yen6GA5z99IQRRpGnSkJPOKN")

print(f"Using endpoint: {PROJECT_ENDPOINT}")
print(f"Using agent: {AGENT_ID}")

# ---- AUTH (AAD ONLY) ----
credential = DefaultAzureCredential()
project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)
agent = project.agents.get_agent(AGENT_ID)

# ---- FASTAPI SETUP ----
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat")
async def chat(payload: dict):
    message = (payload.get("message") or "").strip()
    thread_id = payload.get("thread_id")

    if not message:
        return JSONResponse({"error": "Empty message"}, status_code=400)

    # New or existing thread
    if thread_id:
        thread = project.agents.threads.get(thread_id)
    else:
        thread = project.agents.threads.create()

    # Add user message
    project.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=message
    )

    # Run agent
    run = project.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id
    )

    if run.status == "failed":
        return JSONResponse(
            {"error": str(run.last_error) if run.last_error else "Run failed"},
            status_code=500,
        )

    # Latest assistant message
    messages = list(project.agents.messages.list(thread_id=thread.id))
    assistant_msgs = [
        m for m in messages
        if m.role == "assistant"
        and m.content
        and getattr(m.content[0], "text", None)
        and getattr(m.content[0].text, "value", None)
    ]

    if not assistant_msgs:
        return {"reply": "No response from AURA.", "thread_id": thread.id}

    latest = max(assistant_msgs, key=lambda m: getattr(m, "created_at", 0))
    reply = latest.content[0].text.value

    return {"reply": reply, "thread_id": thread.id}