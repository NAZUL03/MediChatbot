import streamlit as st
from datetime import datetime
import logging

from groq import Groq
from config import Config

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Groq Client (lazy loaded to allow Streamlit secrets to be available)
client = None

def get_client():
    global client
    if client is None:
        api_key = Config.get_groq_api_key()
        client = Groq(api_key=api_key)
    return client

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

# Healthcare Chatbot Class
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

            # Request to Groq
            response = get_client().chat.completions.create(
                model="llama-3.3-70b-versatile",        # Groq's latest Llama model
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
            error_msg = str(e)
            print(f"❌ Groq Error: {error_msg}")
            logger.error(f"Groq API Error: {error_msg}")
            
            # Provide better error messages
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                return "API key error. Please ensure the Groq API key is properly configured in Streamlit secrets."
            elif "rate" in error_msg.lower():
                return "Rate limit exceeded. Please wait a moment and try again."
            else:
                return f"Error: {error_msg[:100] if len(error_msg) > 100 else error_msg}"

# Create chatbot instance
chatbot = OpenAIHealthcareChatbot()

# Streamlit Interface
def chat_interface():
    # Session state to remember conversation history
    if 'chat_initialized' not in st.session_state:
        chatbot.initialize_conversation()
        st.session_state.chat_initialized = True
        st.session_state.conversation_start = datetime.now().isoformat()

    st.title("MediMate Healthcare Chatbot 🩺🤖")
    
    # Debug info in expander
    with st.expander("🔧 Debug Info"):
        api_key = Config.get_groq_api_key()
        if api_key:
            st.success(f"✅ Groq API Key loaded: {api_key[:10]}...")
        else:
            st.error("❌ Groq API Key not found. Please add GROQ_API_KEY to Streamlit secrets.")

    # Display the conversation history
    for message in chatbot.conversation_history:
        if message["role"] == "assistant":
            st.markdown(f"**Assistant:** {message['content']}")
        else:
            st.markdown(f"**You:** {message['content']}")

    # Input text box for user message
    user_message = st.text_input("Your message:", "")

    if user_message:
        # Get chatbot's reply
        bot_reply = chatbot.get_chat_response(user_message)
        st.markdown(f"**Assistant:** {bot_reply}")

# Start new chat
def new_chat():
    chatbot.initialize_conversation()
    st.session_state.conversation_start = datetime.now().isoformat()
    st.success("New conversation started! 👋")

# Streamlit App main
def main():
    st.sidebar.title("Options")
    option = st.sidebar.radio("Select an action", ("Chat", "New Chat"))

    if option == "Chat":
        chat_interface()
    elif option == "New Chat":
        new_chat()

if __name__ == "__main__":
    print("🚀 Starting MediMate Healthcare Chatbot (Groq Version)...")
    print("🤖 Using Groq Llama-3.3-70b")
    api_key = Config.get_groq_api_key()
    print(f"🔑 GROQ KEY LOADED: {api_key[:6]}********")
    print("🌍 https://medichatbot-hu35xsasjg4ejgw9bt2qpq.streamlit.app/")
    st.set_page_config(page_title="MediMate Healthcare Chatbot", layout="wide")
    main()
