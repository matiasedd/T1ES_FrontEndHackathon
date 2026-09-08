import requests

BASE_PATH = "http://localhost:8000"

def get(endpoint: str, params=None):
    response = requests.get(f"{BASE_PATH}{endpoint}", params=params)
    return response.json()

def post(endpoint: str, data=None):
    response = requests.post(f"{BASE_PATH}{endpoint}", json=data)
    return response.json()
