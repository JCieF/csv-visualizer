"""
utils/gemini_client.py

Thin wrapper around the Google Gemini API.

Usage:
    Set GOOGLE_API_KEY in your environment (or a .env file).
    Call generate_insights(stats_summary) with the dict from utils/insights.py.
    Returns a plain-text narrative string, or "" if unavailable.

The function sends only pre-computed statistics (never raw CSV rows) to keep
payloads small, minimise latency, and reduce hallucination risk.
"""

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# Model to use — Flash is fast, generous free-tier, and sufficient for this task
GEMINI_MODEL = "gemini-2.0-flash"

# Maximum output tokens — 3-5 insight sentences fit comfortably in 300 tokens
MAX_OUTPUT_TOKENS = 400


def generate_insights(stats_summary: dict[str, Any]) -> str:
    """
    Send a compact stats summary to Gemini Flash and return a narrative string.

    Args:
        stats_summary: The dict produced by utils/insights._build_stats_summary().

    Returns:
        A plain-text narrative with 3-5 data insights, or an empty string if the
        API key is missing, the call fails, or the response is empty.
    """
    api_key = os.environ.get("GOOGLE_API_KEY", "").strip()
    if not api_key:
        logger.info("GOOGLE_API_KEY not set — skipping AI insights.")
        return ""

    try:
        import google.generativeai as genai  # imported lazily so the app works without the package
    except ImportError:
        logger.warning("google-generativeai not installed — skipping AI insights.")
        return ""

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            GEMINI_MODEL,
            generation_config=genai.GenerationConfig(
                max_output_tokens=MAX_OUTPUT_TOKENS,
                temperature=0.3,   # lower = more factual, less creative
            ),
        )
        prompt = _build_prompt(stats_summary)
        response = model.generate_content(prompt)
        return (response.text or "").strip()

    except Exception as exc:
        logger.warning("Gemini insights call failed: %s", exc)
        print(f"[Gemini insights error] {exc}")
        return ""


def answer_question(stats_summary: dict[str, Any], question: str) -> str:
    """
    Answer a user question strictly about the loaded dataset.

    Args:
        stats_summary: The dict produced by utils/insights._build_stats_summary().
        question:      The user's free-text question.

    Returns:
        A plain-text answer grounded in the dataset statistics, or an error
        string if the API is unavailable.  Never returns an empty string so
        the caller can always render feedback.
    """
    api_key = os.environ.get("GOOGLE_API_KEY", "").strip()
    if not api_key:
        return "AI features are unavailable — GOOGLE_API_KEY is not configured."

    try:
        import google.generativeai as genai
    except ImportError:
        return "AI features are unavailable — google-generativeai package is not installed."

    if not question or not question.strip():
        return ""

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            GEMINI_MODEL,
            generation_config=genai.GenerationConfig(
                max_output_tokens=300,
                temperature=0.2,   # lower temperature for factual, grounded answers
            ),
        )
        prompt = _build_qa_prompt(stats_summary, question.strip())
        response = model.generate_content(prompt)
        return (response.text or "").strip()

    except Exception as exc:
        logger.warning("Gemini Q&A call failed: %s", exc)
        print(f"[Gemini Q&A error] {exc}")
        return f"Error: {exc}"


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def _build_prompt(stats: dict[str, Any]) -> str:
    """
    Construct the Gemini prompt from the pre-computed stats summary.

    The prompt is structured so that Gemini only needs to synthesise
    and narrate — the numbers come from our trusted local computation.
    """
    stats_json = json.dumps(stats, indent=2)

    return f"""You are a friendly data analyst helping a non-technical user understand their CSV dataset.

Here are pre-computed statistics and detected patterns for the file "{stats.get('filename', 'dataset')}":

{stats_json}

Based ONLY on the statistics above, write exactly 3 to 5 concise insights.

Rules:
- Be specific: mention exact column names and numbers from the stats above.
- Focus on the most interesting or actionable patterns (correlations, anomalies, distributions).
- Use plain English — no jargon, no markdown headers, no bullet symbols.
- Number each insight (1. 2. 3. …).
- Keep each insight to 1–2 sentences.
- Do NOT invent numbers that are not in the statistics above.

Insights:"""


def _build_qa_prompt(stats: dict[str, Any], question: str) -> str:
    """
    Build a strict, data-only Q&A prompt for the Gemini model.

    The system instruction confines the model to the provided statistics and
    directs it to politely decline any question that is not about the dataset.
    """
    stats_json = json.dumps(stats, indent=2)

    return f"""You are a data assistant answering questions about a specific CSV dataset.

Here are the pre-computed statistics for the file "{stats.get('filename', 'dataset')}":

{stats_json}

User question: {question}

Instructions:
- Answer ONLY if the question is about THIS dataset (its columns, values, statistics, or patterns shown above).
- Base your answer strictly on the statistics provided — do NOT invent numbers or facts.
- Be concise: 1–3 sentences maximum.
- Use plain English, no markdown formatting.
- If the question is not about the data (e.g. general knowledge, coding, other topics), reply with exactly: "I can only answer questions about the loaded dataset."

Answer:"""
