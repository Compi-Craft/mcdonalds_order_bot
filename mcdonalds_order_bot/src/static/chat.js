document.addEventListener("DOMContentLoaded", () => {
  localStorage.removeItem("session_id");
  let session_id = crypto.randomUUID();
  localStorage.setItem("session_id", session_id);

  const greeting = "👋 Welcome to McDonald's! What can I get you started with?";
  appendMessage("🤖 " + greeting, "bot");

    document.getElementById("chat-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const input = document.getElementById("user-input");
        const user_msg = input.value;
        appendMessage("🧑 You: " + user_msg, "user");
        input.value = "";

        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id, user_input: user_msg })
        });
        const data = await res.json();
        appendMessage("🤖 " + data.response, "bot");
    });

    function appendMessage(text, cls) {
        const chat = document.getElementById("chat");
        const msg = document.createElement("div");
        msg.innerHTML = text.replace(/\n/g, "<br>");
        msg.className = "msg " + cls;
        chat.appendChild(msg);
        chat.scrollTop = chat.scrollHeight;
    }
});

