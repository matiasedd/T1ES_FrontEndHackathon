from datetime import datetime
import requests

BASE_PATH = "http://localhost:8000"

def get(endpoint: str):
    response = requests.get(f"{BASE_PATH}{endpoint}")
    return response.json()
