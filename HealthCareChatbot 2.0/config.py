import os
from dotenv import load_dotenv

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

load_dotenv()  # Load .env file

class Config:
    @staticmethod
    def get_groq_api_key():
        # First try Streamlit secrets (for cloud deployment)
        if STREAMLIT_AVAILABLE:
            try:
                key = st.secrets.get("GROQ_API_KEY")
                if key:
                    return key
            except (KeyError, AttributeError, FileNotFoundError):
                pass
        # Fall back to environment variable (for local development)
        key = os.getenv("GROQ_API_KEY")
        if key:
            return key
        return None
    
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    @classmethod
    def validate(cls):
        if not cls.get_groq_api_key():
            raise ValueError("GROQ_API_KEY missing in .env or Streamlit secrets")
