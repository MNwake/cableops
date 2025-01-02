import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

INFURA_API_KEY = os.getenv("INFURA_API_KEY", "2bd2472a7cd64efc91421cd7b1d772a9")
NETWORK_URL = f"https://sepolia.infura.io/v3/{INFURA_API_KEY}"  # Use Sepolia for testing
