const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("input");
const sendBtn = document.getElementById("send");
const promptButtons = document.querySelectorAll(".prompt-btn");

let threadId = null;

/**
 * Append a chat bubble to the UI.
 */
function appendMessage(role, text) {
  const msg = document.createElement("div");
  msg.className = "msg " + (role === "user" ? "msg-user" : "msg-bot");

  const avatar = document.createElement("div");
  avatar.className =
    "avatar " + (role === "user" ? "avatar-user" : "avatar-bot");
  avatar.textContent = role === "user" ? "U" : "A";

  const bubble = document.createElement("div");
  bubble.className =
    "bubble " + (role === "user" ? "bubble-user" : "bubble-bot");

  if (role === "assistant") {
    const formatted = formatReply(text);
    bubble.innerHTML = marked.parse(formatted);
  } else {
    bubble.textContent = text;
  }

  msg.appendChild(avatar);
  msg.appendChild(bubble);
  messagesEl.appendChild(msg);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

/**
 * Cleaning up AURA's raw reply
 */
function formatReply(raw) {
  if (!raw) return "No response available.";

  let text = String(raw);

  console.log("RAW AURA REPLY:", text); // debug

  // Remove any bracketed chunks that contain 'source'
  text = text.replace(/\[[^\]]*source[^\]]*\]/gi, "");

  // Remove simple numeric references like [1], [2]
  text = text.replace(/\[\d+\]/g, "");

  // Normalize whitespace
  text = text
    .replace(/[ \t]+/g, " ")
    .replace(/\r\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();

  // Highlighting recommendations
  text = text.replace(/recommendation:\s*/i, "\n\n**Recommendation:** ");

  return text.trim();
}

/**
 * Send a message to the FastAPI backend and display the response.
 */
async function sendMessage(textOverride) {
  const text = (textOverride ?? inputEl.value).trim();
  if (!text) return;

  appendMessage("user", text);
  inputEl.value = "";
  inputEl.focus();

  // Temporary "thinking" message
  const thinking = document.createElement("div");
  thinking.className = "msg msg-bot";
  const avatar = document.createElement("div");
  avatar.className = "avatar avatar-bot";
  avatar.textContent = "A";
  const bubble = document.createElement("div");
  bubble.className = "bubble bubble-bot";
  bubble.textContent = "AURA is thinking";
  thinking.appendChild(avatar);
  thinking.appendChild(bubble);
  messagesEl.appendChild(thinking);
  messagesEl.scrollTop = messagesEl.scrollHeight;

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, thread_id: threadId }),
    });

    const data = await res.json();
    messagesEl.removeChild(thinking);

    if (res.ok && data.reply) {
      threadId = data.thread_id || threadId;
      appendMessage("assistant", data.reply);
    } else {
      appendMessage(
        "assistant",
        "I couldn’t process that. Try rephrasing your question."
      );
    }
  } catch (err) {
    console.error("Chat error:", err);
    messagesEl.removeChild(thinking);
    appendMessage(
      "assistant",
      "Network error. Ensure the AURA backend is running."
    );
  }
}

/**
 * Event bindings
 */
sendBtn.addEventListener("click", () => sendMessage());

inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});

promptButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    const q = btn.getAttribute("data-q");
    sendMessage(q);
  });
});