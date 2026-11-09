# Agentic WebApp Generator

An agentic code-generation service built with LangGraph, FastAPI and Mistral AI. Given an application specification, it generates a Streamlit application, a FastAPI backend, and an HTML frontend that consumes that backend.

## How it works

1. **GenSystemPrompts** reads the specification and produces tailored system prompts for each generator.
2. **GenFastApiCode** and **GenStreamlitCode** run in parallel to produce the backend and the Streamlit app.
3. **GenHtmlCode** produces the HTML frontend using the generated FastAPI code, so the endpoints match.

## Project structure

```
.
├── agent.py              # LangGraph pipeline definition
├── main.py               # FastAPI application and routes
├── schema/payload.py     # Request and response models
├── state/StatePipeline.py# Shared pipeline state
├── tools/nodes.py        # LLM nodes and prompt templates
├── requirements.txt
├── .env.example
└── Dockerfile
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then add your MISTRAL_API_KEY
```

## Run locally

```bash
uvicorn main:app --reload
```

The API is available at `http://127.0.0.1:8000`, and interactive docs are at `/docs`.

## API

| Method | Endpoint        | Description                                      |
|--------|-----------------|--------------------------------------------------|
| GET    | `/api/health`   | Liveness check                                   |
| POST   | `/api/generate` | Generates code from `payload_with_models` (5 requests per minute per client) |

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"payload_with_models": "A todo app with add, complete and delete actions"}'
```

## Configuration

| Variable          | Required | Description                                                        |
|-------------------|----------|--------------------------------------------------------------------|
| `MISTRAL_API_KEY` | Yes      | API key for Mistral AI                                             |
| `ALLOWED_ORIGINS` | No       | Comma-separated CORS origins. Defaults to `*`; restrict in production. |

## Docker

```bash
docker build -t agentic-webapp-generator .
docker run -p 8000:8000 --env-file .env agentic-webapp-generator
```

## Notes for production

- Set `ALLOWED_ORIGINS` to your frontend's domain(s) instead of `*`.
- Rate limiting uses the client IP address. If the service runs behind a reverse proxy or load balancer, configure the proxy to forward the real client IP and adjust `key_func` accordingly.
- Pin exact dependency versions in `requirements.txt` after testing in your environment.
- Serve the frontend from a `static/` directory next to `main.py`. It is mounted automatically when present.
