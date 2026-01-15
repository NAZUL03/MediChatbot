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
        if not api_key:
            raise ValueError(
                "❌ GROQ_API_KEY is missing!\n\n"
                "On Streamlit Cloud:\n"
                "1. Click ☰ menu → Settings\n"
                "2. Add to Secrets:\n"
                '   GROQ_API_KEY = "gsk_..."\n'
                "3. Click Reboot app\n\n"
                "Locally: Add GROQ_API_KEY to .env file"
            )
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

            bot_reply = response.choices[0].message.content

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

    # Page config
    st.set_page_config(page_title="MediMate", layout="centered", initial_sidebar_state="collapsed")
    
    # Custom CSS for chatbot styling
    st.markdown("""
    <style>
        .chat-container {
            max-width: 800px;
            margin: 0 auto;
        }
        .message-box {
            padding: 12px 16px;
            border-radius: 12px;
            margin: 8px 0;
            word-wrap: break-word;
        }
        .user-message {
            background-color: #007AFF;
            color: white;
            margin-left: auto;
            margin-right: 0;
            width: fit-content;
            max-width: 70%;
            border-radius: 18px 4px 18px 18px;
        }
        .assistant-message {
            background-color: #E8E8EA;
            color: #000;
            margin-right: auto;
            margin-left: 0;
            width: fit-content;
            max-width: 70%;
            border-radius: 4px 18px 18px 18px;
        }
        .chat-header {
            text-align: center;
            padding: 20px 0;
            border-bottom: 2px solid #E8E8EA;
            margin-bottom: 20px;
        }
        .input-container {
            display: flex;
            gap: 10px;
            margin-top: 20px;
            border-top: 2px solid #E8E8EA;
            padding-top: 15px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="chat-header">
        <h1>🩺 MediMate Healthcare Chatbot</h1>
        <p style="color: #888; margin-top: -15px;">Your AI Healthcare Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display the conversation history with better formatting
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    for message in chatbot.conversation_history:
        if message["role"] == "assistant":
            st.markdown(f'<div class="message-box assistant-message">🤖 {message["content"]}</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="message-box user-message">👤 {message["content"]}</div>', 
                       unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input area with better styling
    st.markdown('<hr style="margin: 20px 0">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_message = st.text_input(
            "Type your message...",
            placeholder="Ask me about health, wellness, or medical topics...",
            label_visibility="collapsed",
            key="user_input"
        )
    
    with col2:
        send_button = st.button("Send ➤", use_container_width=True)
    
    if send_button and user_message:
        # Get chatbot's reply
        with st.spinner("🤖 Thinking..."):
            bot_reply = chatbot.get_chat_response(user_message)
        st.rerun()
    
    # Debug info in sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        with st.expander("🔧 Debug Info"):
            api_key = Config.get_groq_api_key()
            if api_key:
                st.success(f"✅ Groq API Key loaded")
            else:
                st.error("❌ Groq API Key not found")

# Start new chat
def new_chat():
    chatbot.initialize_conversation()
    st.session_state.conversation_start = datetime.now().isoformat()
    st.success("New conversation started! 👋")

# Streamlit App main
def main():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "chat"
    
    # Sidebar menu
    with st.sidebar:
        st.markdown("### 🏠 Menu")
        if st.button("💬 New Chat", use_container_width=True):
            chatbot.initialize_conversation()
            st.session_state.current_page = "chat"
            st.rerun()
    
    chat_interface()

if __name__ == "__main__":
    # Set page config first
    st.set_page_config(
        page_title="MediMate Healthcare Chatbot",
        page_icon="🩺",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    print("🚀 Starting MediMate Healthcare Chatbot (Groq Version)...")
    print("🤖 Using Groq Llama-3.3-70b")
    api_key = Config.get_groq_api_key()
    print(f"🔑 GROQ KEY LOADED: {api_key[:6] if api_key else 'NOT FOUND'}...")
    print("🌍 https://medichatbot-hu35xsasjg4ejgw9bt2qpq.streamlit.app/")
    main()
