import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'HealthCareChatbot 2.0'))

# Import and run the main app
from app import main

if __name__ == "__main__":
    main()
