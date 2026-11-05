from fastapi import FastAPI
from pydantic import BaseModel
import requests
app = FastAPI()
Ollama_URL = "http://localhost:11434/api/generate"

class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
def home():
    return{"message": "My first API application"}
@app.post("/predict")
def predict(request: PromptRequest):
    response = requests.post(Ollama_URL, json={
        "model": "llama3.2:1b",
        "prompt": request.prompt,
        "stream": False
    })
    data = response.json()
    return {"ai_response": data["response"]}
