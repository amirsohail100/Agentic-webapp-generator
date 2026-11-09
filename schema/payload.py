from typing import List

from pydantic import BaseModel


class GenerateRequest(BaseModel):
    """Incoming request carrying the application specification."""

    payload_with_models: str


class GenerateResponse(BaseModel):
    """Generated artifacts returned to the client."""

    llm_gen_system_prompts: List[dict]
    fastapi_code: str
    streamlit_code: str
    html_code: str
