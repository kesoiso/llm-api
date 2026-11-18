from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException,Response
import time
import requests
import os
app = FastAPI()
REQUEST_COUNT = Counter("predict_requests_total", "Total requests to /predict")
ERROR_COUNT = Counter("predict_errors_total", "Total failed requests to /predict")
LATENCY = Histogram("predict_latency_seconds", "Time taken by /predict",buckets=[5, 10, 20, 30, 60, 120] )

Ollama_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
def home():
    return{"message": "My first API application"}
@app.post("/predict")
def predict(request: PromptRequest):
    REQUEST_COUNT.inc()
    start = time.time()
    try:
        response = requests.post(Ollama_URL, json={
            "model": "llama3.2:1b",
            "prompt": request.prompt,
            "stream": False
        })
    except requests.exceptions.ConnectionError:
        ERROR_COUNT.inc()
        raise HTTPException(status_code=503, detail="Model server is unavailable. Please try again later")
    end = time.time()
    LATENCY.observe(end - start)

    data = response.json()
    tokens = data["eval_count"]
    gen_seconds = data["eval_duration"] / 1_000_000_000
    tokens_per_second = round(tokens / gen_seconds, 2)

    return {"ai_response": data["response"],
            "latency_seconds": round(end - start, 2),
            "tokens_generated": tokens,
            "tokens_per_second": tokens_per_second
            }
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)