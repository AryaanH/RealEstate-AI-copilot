from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint="https://real-estate-ai-resource.services.ai.azure.com/api/projects/real-estate-ai"
)

agent = project.agents.get_agent("asst_mNSYbCoZ58f61IbiWlb0JVou")
print("AURA — Real-Estate AI Copilot is active. Type 'exit' to quit.")

# One thread per chat session
thread = project.agents.threads.create()

while True:
    user_input = input("\nYou: ").strip()
    if user_input.lower() == "exit":
        break

    # 1) Add user message
    project.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )

    # 2) Run the agent
    run = project.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id
    )

    if run.status == "failed":
        print("Run failed:", run.last_error)
        continue

    # 3) Fetch messages (no 'order' arg => works across SDK versions)
    msgs = list(project.agents.messages.list(thread_id=thread.id))

    # filter assistant msgs that have text content
    assistant_msgs = [
        m for m in msgs
        if m.role == "assistant"
        and m.content
        and getattr(m.content[0], "text", None)
        and getattr(m.content[0].text, "value", None)
    ]

    if assistant_msgs:
        # pick the latest by created_at (works across SDK versions)
        latest = max(assistant_msgs, key=lambda m: getattr(m, "created_at", 0))
        print("AURA:", latest.content[0].text.value)
    else:
        print("AURA: (no content)")
