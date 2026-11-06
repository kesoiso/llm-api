from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
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
    try:
        response = requests.post(Ollama_URL, json={
            "model": "llama3.2:1b",
            "prompt": request.prompt,
            "stream": False
        })
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Model server is unavailable. Please try again later")
    data = response.json()
    return {"ai_response": data["response"]}
