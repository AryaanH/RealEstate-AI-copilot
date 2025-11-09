from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# --- loading env from config---
load_dotenv('config/.env')

PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
AGENT_ID = os.getenv("AGENT_ID")


if not PROJECT_ENDPOINT or not AGENT_ID:
    raise RuntimeError("PROJECT_ENDPOINT and AGENT_ID must be set.")


credential = DefaultAzureCredential()
project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)
agent = project.agents.get_agent(AGENT_ID)

# FastAPI
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        # 1) thread
        thread_id = req.thread_id
        if not thread_id:
            thread = project.agents.threads.create()
            thread_id = thread.id

        # 2) user msg
        project.agents.messages.create(
            thread_id=thread_id,
            role="user",
            content=req.message,
        )

        # 3) run
        run = project.agents.runs.create_and_process(
            thread_id=thread_id,
            agent_id=agent.id,
        )
        if run.status == "failed":
            raise HTTPException(status_code=500, detail=str(run.last_error))

        # 4) recent assistant msg
        msgs = list(project.agents.messages.list(thread_id=thread_id))
        assistant_msgs = [
            m for m in msgs
            if m.role == "assistant"
            and m.content
            and getattr(m.content[0], "text", None)
            and getattr(m.content[0].text, "value", None)
        ]

        if not assistant_msgs:
            raise HTTPException(status_code=500, detail="No assistant reply.")

        latest = max(assistant_msgs, key=lambda m: getattr(m, "created_at", 0))
        reply = latest.content[0].text.value

        return {"reply": reply, "thread_id": thread_id}

    except HTTPException:
        raise
    except Exception as e:
        # surface real error while we’re debugging
        raise HTTPException(status_code=500, detail=str(e))