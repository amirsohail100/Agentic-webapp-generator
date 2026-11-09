from typing import List, TypedDict


class State(TypedDict):
    """State shared between all nodes of the generation pipeline."""

    payload_with_models: str
    llm_gen_system_prompts: List[dict]
    html_code: str
    fastapi_code: str
    streamlit_code: str
