"""LangGraph pipeline that turns an application specification into web app code."""

from langgraph.graph import END, START, StateGraph

from state.StatePipeline import State
from tools.nodes import (
    GenFastApiCode_node,
    GenHtmlCode_node,
    GenStreamlitCode_node,
    GenSystemPrompts_node,
)

_graph = StateGraph(State)

_graph.add_node("GenSystemPrompts", GenSystemPrompts_node)
_graph.add_node("GenFastApiCode", GenFastApiCode_node)
_graph.add_node("GenStreamlitCode", GenStreamlitCode_node)
_graph.add_node("GenHtmlCode", GenHtmlCode_node)

_graph.add_edge(START, "GenSystemPrompts")

# The FastAPI and Streamlit generators run in parallel once the prompts exist.
_graph.add_edge("GenSystemPrompts", "GenFastApiCode")
_graph.add_edge("GenSystemPrompts", "GenStreamlitCode")

# The HTML generator needs the FastAPI code so it can call the correct endpoints.
_graph.add_edge("GenFastApiCode", "GenHtmlCode")

_graph.add_edge("GenHtmlCode", END)
_graph.add_edge("GenStreamlitCode", END)

APP = _graph.compile()


def RunPipeline(payload_with_models: str) -> dict:
    """Run the full generation pipeline and return the resulting state."""
    return APP.invoke({"payload_with_models": payload_with_models})
