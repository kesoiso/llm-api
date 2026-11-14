# llm-api

A FastAPI service that serves an open-source LLM (`llama3.2:1b` via Ollama) and measures its performance on every request: latency, tokens generated, and tokens/sec. Containerized with Docker, built and pushed by GitHub Actions, and deployed on an Azure VM (CPU only).

## Architecture

```
Browser
 → NSG (Azure firewall: allows only my IP on port 8000)
 → VM:8000
 → Container (--network host, so the VM's 8000 = uvicorn's 8000)
 → Uvicorn (server, runs the app)
 → FastAPI (finds /predict; Pydantic checks the request body)
 → predict() → requests.post()
 → Ollama (localhost:11434, llama3.2:1b)
 → answer + metrics back to the browser
```

## Tech stack

- **Model:** llama3.2:1b, served by Ollama
- **API:** Python, FastAPI, Uvicorn, Pydantic
- **Container:** Docker, Docker Hub (`kesoiso/llm-api`)
- **CI/CD:** GitHub Actions
- **Cloud:** Azure VM (Ubuntu 24.04, 2 vCPU, 4 GB RAM, CPU only)

## How to run it

You need [Ollama](https://ollama.com) running with the model: `ollama pull llama3.2:1b`

**1. Laptop (Python)**
```bash
python -m venv venv
source venv/Scripts/activate    # Windows Git Bash
pip install -r requirements.txt
uvicorn main:app --reload
```
Open http://127.0.0.1:8000/docs

**2. Laptop (Docker Compose)**
```bash
docker compose up --build
```
Open http://127.0.0.1:5000/docs

**3. Linux server / cloud VM (image from Docker Hub)**
```bash
docker run -d --name llm-api --network host --restart unless-stopped \
  -e OLLAMA_URL=http://localhost:11434/api/generate \
  kesoiso/llm-api
```
Open http://<SERVER_IP>:8000/docs

### Example request
```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is Docker?"}'
```

### Example response
```json
{
  "ai_response": "...",
  "latency_seconds": 20.66,
  "tokens_generated": 67,
  "tokens_per_second": 8.93
}
```

## Results (CPU only, no GPU)

| Where | Latency | Tokens/sec | Note |
|---|---|---|---|
| Laptop (cold start) | 51 s | — | model loading |
| Laptop (warm start) | 7 s | ~8–10 | model already loaded |
| Laptop (Docker Hub image) | 13.17 s | 8.38 | 31 tokens |
| Azure VM (cold) | 110.37 s | 8.16 | 731 tokens, ~17.5 s model load |
| Azure VM (after reboot) | 20.66 s | 8.93 | 67 tokens, 13.16 s overhead |

**Key findings**
- Cold start is the biggest delay (up to 51 s on the laptop).
- A 2 vCPU cloud VM is about as fast as my laptop: ~8–9 tokens/sec on CPU.

## What I learned

- Debugging a 503: the VM got traffic, but the container couldn't reach Ollama because of a typo in an env variable. Lesson: check, don't assume.
- Docker: build once, run anywhere (laptop, CI runner, cloud VM).
- Environment variables: the same image works in different environments.
- CI/CD with GitHub Actions: every push is tested, built and pushed to Docker Hub automatically.
- Cloud VMs in practice: SSH, firewalls (NSG), ports, auto-restart, cost control.
- HTTP: GET vs POST, status codes (200, 422, 503), JSON and YAML.
- Small models (1B) hallucinate facts, so measure and verify.

## Next steps

- Monitoring with Prometheus + Grafana
- API key + HTTPS
- vLLM on a GPU (Colab/Kaggle) and compare tokens/sec
