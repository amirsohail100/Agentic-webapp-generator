"""FastAPI entrypoint for the Agentic WebApp Generator."""

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from agent import RunPipeline
from schema.payload import GenerateRequest, GenerateResponse

load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agentic WebApp Generator",
    description="Generates Streamlit and HTML/FastAPI web applications from a specification.",
    version="1.0.0",
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Comma-separated list of allowed origins, e.g. "https://example.com,https://app.example.com".
# Defaults to "*" for development; set ALLOWED_ORIGINS in production.
allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    """Return a simple liveness status for monitoring and load balancers."""
    return {"status": "ok"}


@app.post("/api/generate", response_model=GenerateResponse)
@limiter.limit("5/minute")
def generate(request: Request, payload: GenerateRequest):
    """Generate Streamlit, FastAPI and HTML code from the given specification."""
    if not payload.payload_with_models.strip():
        raise HTTPException(
            status_code=400,
            detail="payload_with_models must not be empty.",
        )

    try:
        results = RunPipeline(payload.payload_with_models)
    except Exception as exc:
        logger.exception("Code generation pipeline failed.")
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return GenerateResponse(
        llm_gen_system_prompts=results["llm_gen_system_prompts"],
        fastapi_code=results["fastapi_code"],
        streamlit_code=results["streamlit_code"],
        html_code=results["html_code"],
    )


# Serve the frontend only when the static directory exists, so the API can start without it.
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
