import os
import chainlit as cl
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient

load_dotenv()
endpoint = os.getenv("PROJECT_ENDPOINT")
agent_id = os.getenv("AGENT_ID")


@cl.on_chat_start
async def start():
    client = AgentsClient(
        endpoint=endpoint, credential=DefaultAzureCredential())
    cl.user_session.set("client", client)
    await cl.Message(content="**Aryaan’s RealEstate Copilot** is LIVE 🏠\nAsk me anything!").send()


@cl.on_message
async def main(message: cl.Message):
    client = cl.user_session.get("client")

    # 1. Create thread once
    thread = cl.user_session.get("thread")
    if not thread:
        thread = await client.threads.create()
        cl.user_session.set("thread", thread)

    # 2. Send your question
    await client.messages.create(
        thread_id=thread.id,
        role="user",
        content=message.content
    )

    # 3. Stream answer (the ONLY working way today)
    response = cl.Message(content="")
    await response.send()

    run = await client.runs.create(thread_id=thread.id, agent_id=agent_id)
    async for event in client.runs.stream(run.id):
        if event.event == "thread.message.delta" and event.delta.text:
            await response.stream_token(event.delta.text)
        # Show [1][2] citations from your PDFs
        if event.event == "thread.message.completed":
            msg = await client.messages.get(thread.id, event.message.id)
            for i, anno in enumerate(msg.annotations or [], 1):
                if anno.type == "file_citation":
                    await response.stream_token(f"[{i}]")

    await response.update()

load_dotenv()

client = AgentsClient(
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential()
)


@cl.on_chat_start
async def ():
    await cl.Message("🏠 **Aryaan’s RealEstate Copilot** is LIVE\nAsk me anything!").send()


@cl.on_message
async def (msg: cl.Message):
    # 1. ONE-LINE thread
    thread = await client.threads.create() if not cl.user_session.get("thread_id") else cl.user_session.get("thread")
    if not cl.user_session.get("thread_id"):
        cl.user_session.set("thread_id", thread.id)

    # 2. ONE-LINE message
    await client.messages.create(thread_id=thread.id, role="user", content=msg.content)

    # 3. ONE-LINE stream
    reply = cl.Message(content="")
    await reply.send()
    async for chunk in client.runs.stream_expanded(thread_id=thread.id, agent_id=os.getenv("AGENT_ID")):
        if chunk.data.get("delta", {}).get("content"):
            await reply.stream_token(chunk.data["delta"]["content"][0]["text"]["value"])
    await reply.update()
