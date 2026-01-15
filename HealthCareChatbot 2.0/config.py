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
    def get_openai_api_key():
        # First try Streamlit secrets (for cloud deployment)
        if STREAMLIT_AVAILABLE:
            try:
                return st.secrets["OPENAI_API_KEY"]
            except (KeyError, AttributeError):
                pass
        # Fall back to environment variable (for local development)
        return os.getenv("OPENAI_API_KEY")
    
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    @classmethod
    def validate(cls):
        if not cls.get_openai_api_key():
            raise ValueError("OPENAI_API_KEY missing in .env or Streamlit secrets")
