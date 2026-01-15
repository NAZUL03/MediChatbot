from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import logging
from config import Config
from openai import OpenAI

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
# ================================
# OPENAI CLIENT
# ================================
client = OpenAI(api_key=Config.OPENAI_API_KEY)

# System prompt for healthcare chatbot
SYSTEM_PROMPT = """
You are MediMate, an AI healthcare assistant.

Rules:
🩺 Provide general health guidance only
⚠️ Do NOT diagnose diseases
🚑 Recommend seeing a doctor for serious symptoms
💊 Provide safe wellness & lifestyle suggestions
😊 Be friendly, supportive, and clear

Keep responses short, helpful, and easy to read.
"""

# ================================
# HEALTHCARE CHATBOT (OPENAI)
# ================================
class OpenAIHealthcareChatbot:
    def __init__(self):
        self.conversation_history = []

    def initialize_conversation(self):
        self.conversation_history = [
            {
                "role": "assistant",
                "content": "Hello! I'm MediMate, your AI healthcare assistant 🤖🩺 How can I help you today?"
            }
        ]

    def add_message(self, role, content):
        self.conversation_history.append({"role": role, "content": content})

    def get_chat_response(self, user_message):
        try:
            self.add_message("user", user_message)

            # Build OpenAI messages
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.conversation_history

            # Request to OpenAI
            response = client.chat.completions.create(
                model="gpt-4o-mini",        # Change model here if needed
                messages=messages
            )

            bot_reply = response.choices[0].message["content"]

            self.add_message("assistant", bot_reply)

            # Limit history size
            if len(self.conversation_history) > 14:
                self.conversation_history = (
                    [self.conversation_history[0]] +
                    self.conversation_history[-12:]
                )

            return bot_reply

        except Exception as e:
            print(f"❌ OpenAI Error: {e}")
            return "I'm having trouble connecting to OpenAI. Please try again."

# Create chatbot instance
chatbot = OpenAIHealthcareChatbot()

# ================================
# ROUTES
# ================================
@app.route('/')
def home():
    if "chat_initialized" not in session:
        chatbot.initialize_conversation()
        session["chat_initialized"] = True
        session["conversation_start"] = datetime.now().isoformat()

    return render_template("index.html")

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"error": "Empty message"}), 400

        bot_reply = chatbot.get_chat_response(user_message)

        return jsonify({
            "reply": bot_reply,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/new_chat', methods=['POST'])
def new_chat():
    chatbot.initialize_conversation()
    session["conversation_start"] = datetime.now().isoformat()

    return jsonify({
        "status": "success",
        "message": "New conversation started",
        "welcome_message": chatbot.conversation_history[0]["content"]
    })

@app.route('/test')
def test_api():
    """Test OpenAI connection"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say only: 'OpenAI API is working!'"}]
        )

        reply = response.choices[0].message["content"]

        return jsonify({
            "status": "success",
            "message": "OpenAI API is working 🎉",
            "response": reply
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"OpenAI Test Failed: {e}"
        })

if __name__ == "__main__":
    print("🚀 Starting MediMate Healthcare Chatbot (OpenAI Version)...")
    print("🤖 Using OpenAI GPT-4o-mini")
    print(f"🔑 OPENAI KEY LOADED: {Config.OPENAI_API_KEY[:6]}********")
    print("🌍 http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
