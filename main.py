
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import time
import request
import os
app = FastAPI()
Ollama_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
def home():
    return{"message": "My first API application"}
@app.post("/predict")
def predict(request: PromptRequest):
    start = time.time()
    try:
        response = requests.post(Ollama_URL, json={
            "model": "llama3.2:1b",
            "prompt": request.prompt,
            "stream": False
        })
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Model server is unavailable. Please try again later")
    end = time.time()

    data = response.json()
    tokens = data["eval_count"]
    gen_seconds = data["eval_duration"] / 1_000_000_000
    tokens_per_second = round(tokens / gen_seconds, 2)

    return {"ai_response": data["response"],
            "latency_seconds": round(end - start, 2),
            "tokens_generated": tokens,
            "tokens_per_second": tokens_per_second
            }
