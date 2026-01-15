document.addEventListener("DOMContentLoaded", () => {
    const chatMessages = document.getElementById("chatMessages");
    const messageInput = document.getElementById("messageInput");
    const sendButton = document.getElementById("sendButton");
    const typingIndicator = document.getElementById("typingIndicator");
    const newChatBtn = document.getElementById("newChatBtn");

    function addMessage(text, sender) {
        const msg = document.createElement("div");
        msg.classList.add("message", sender === "user" ? "user-message" : "bot-message");
        msg.innerHTML = text.replace(/\n/g, "<br>");
        chatMessages.appendChild(msg);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showTyping() {
        typingIndicator.style.display = "block";
    }

    function hideTyping() {
        typingIndicator.style.display = "none";
    }

    async function sendMessage() {
        const text = messageInput.value.trim();
        if (!text) return;

        addMessage(text, "user");
        messageInput.value = "";
        showTyping();

        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });

        const data = await res.json();
        hideTyping();

        if (data.reply) {
            addMessage(data.reply, "bot");
        }
    }

    sendButton.addEventListener("click", sendMessage);

    messageInput.addEventListener("keypress", e => {
        if (e.key === "Enter") sendMessage();
    });

    newChatBtn.addEventListener("click", async () => {
        const res = await fetch("/new_chat", { method: "POST" });
        const data = await res.json();
        chatMessages.innerHTML = "";
        addMessage(data.welcome_message, "bot");
    });
});
