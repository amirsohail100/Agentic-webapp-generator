"""Pipeline nodes that call the LLM to generate system prompts and application code."""

from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv

from state.StatePipeline import State

load_dotenv()


SYSTEM_PROMPTS_TEMPLATE = """You are an expert prompt engineer. Read the application specification below and write three detailed system prompts, one for each code generator:
- "fastapi": a system prompt for an agent that writes a complete FastAPI backend.
- "streamlit": a system prompt for an agent that writes a complete Streamlit application.
- "html": a system prompt for an agent that writes a complete, single-file HTML, CSS and JavaScript frontend that calls the FastAPI backend.

Each prompt must be specific, self-contained and complete enough for the agent to work without further input.

Application specification:
{payload_with_models}

Return ONLY a valid JSON object with exactly the keys "html", "fastapi" and "streamlit", where every value is a string. Do not write any text or Markdown outside the JSON object."""

FASTAPI_CODE_TEMPLATE = """{fastapi_system_prompt}

Write the complete FastAPI application now. Requirements:
- Output only valid Python source code, with no explanations before or after it.
- Do not wrap the code in Markdown code fences.
- Include all imports so the file runs with uvicorn.
- Use clear, professional English comments and docstrings."""

HTML_CODE_TEMPLATE = """{html_system_prompt}

The backend is implemented by the following FastAPI code. Make sure the frontend calls its endpoints with the correct paths, HTTP methods and request fields:

{fastapi_code}

Write the complete HTML document now. Requirements:
- Output only the HTML document, with no explanations before or after it.
- Do not wrap the output in Markdown code fences.
- Keep all CSS and JavaScript inside the single HTML file."""

STREAMLIT_CODE_TEMPLATE = """{streamlit_system_prompt}

Write the complete Streamlit application now. Requirements:
- Output only valid Python source code, with no explanations before or after it.
- Do not wrap the code in Markdown code fences.
- Include all imports so the file runs with "streamlit run".
- Use clear, professional English comments and docstrings."""


def strip_code_fences(text: str) -> str:
    """Remove a surrounding Markdown code fence (```lang ... ```) from LLM output, if present."""
    stripped = text.strip()
    if stripped.startswith("```"):
        first_newline = stripped.find("\n")
        stripped = stripped[first_newline + 1:] if first_newline != -1 else ""
        if stripped.rstrip().endswith("```"):
            stripped = stripped.rstrip()[:-3]
    return stripped.strip()


def GenSystemPrompts_node(state: State) -> dict:
    """Generate the FastAPI, Streamlit and HTML system prompts from the specification."""
    llm = ChatMistralAI()

    prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPTS_TEMPLATE)

    chain = prompt | llm | JsonOutputParser()

    response = chain.invoke({
        "payload_with_models": state["payload_with_models"],
    })

    return {
        "llm_gen_system_prompts": [{
            "html": response["html"],
            "fastapi": response["fastapi"],
            "streamlit": response["streamlit"],
        }]
    }


def GenFastApiCode_node(state: State) -> dict:
    """Generate the FastAPI backend code."""
    llm = ChatMistralAI()

    prompt = ChatPromptTemplate.from_template(FASTAPI_CODE_TEMPLATE)

    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({
        "fastapi_system_prompt": state["llm_gen_system_prompts"][0]["fastapi"],
    })

    return {
        "fastapi_code": strip_code_fences(response),
    }


def GenHtmlCode_node(state: State) -> dict:
    """Generate the HTML frontend that consumes the generated FastAPI backend."""
    llm = ChatMistralAI()

    prompt = ChatPromptTemplate.from_template(HTML_CODE_TEMPLATE)

    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({
        "html_system_prompt": state["llm_gen_system_prompts"][0]["html"],
        "fastapi_code": state["fastapi_code"],
    })

    return {
        "html_code": strip_code_fences(response),
    }


def GenStreamlitCode_node(state: State) -> dict:
    """Generate the Streamlit application code."""
    llm = ChatMistralAI()

    prompt = ChatPromptTemplate.from_template(STREAMLIT_CODE_TEMPLATE)

    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({
        "streamlit_system_prompt": state["llm_gen_system_prompts"][0]["streamlit"],
    })

    return {
        "streamlit_code": strip_code_fences(response),
    }
