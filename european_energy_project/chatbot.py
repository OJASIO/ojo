import os
import json
import streamlit as st
from groq import Groq
import sys
sys.path.insert(0, os.path.dirname(__file__))
from db_writer import get_recent_readings, get_anomalies


def get_groq_client() -> Groq:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
        load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in secrets or .env file")
    return Groq(api_key=api_key)


def build_energy_context() -> str:
    """
    Build a concise context string from the database to inject into
    every LLM prompt — this is lightweight RAG without a vector DB.
    """
    readings = get_recent_readings(hours=24)
    anomalies = get_anomalies()

    if not readings:
        return "No energy data available yet. The pipeline is still ingesting data."

    import pandas as pd
    df = pd.DataFrame(readings)

    site_summary = (
        df.groupby("site")["consumption_kw"]
        .agg(["mean", "max", "min", "count"])
        .round(2)
        .to_dict(orient="index")
    )

    anomaly_summary = []
    for a in anomalies[:5]:
        anomaly_summary.append(
            f"- {a['site']} at {a['timestamp']}: {a['anomaly_reason']}"
        )

    context = f"""
You are an energy operations assistant for a global manufacturing company.
You have access to real-time energy consumption data from 5 European sites:
Stuttgart, Munich, Berlin, Hamburg, and Lyon.

CURRENT SITE PERFORMANCE (last 24 hours):
{json.dumps(site_summary, indent=2)}

RECENT ANOMALIES DETECTED:
{chr(10).join(anomaly_summary) if anomaly_summary else "No anomalies detected recently."}

TOTAL READINGS IN DATABASE: {len(readings)}

Use this data to answer questions accurately. When asked about specific sites,
reference the actual numbers. If asked why consumption is high or low,
reason based on the temperature and baseline data available.
Always be concise and actionable in your responses.
"""
    return context


def generate_weekly_report() -> str:
    """Generate an automated platform transparency report using the LLM."""
    client = get_groq_client()
    context = build_energy_context()

    prompt = f"""
{context}

Generate a structured weekly energy operations report with:
1. Executive summary (2 sentences)
2. Site performance ranking (best to worst efficiency)
3. Anomalies detected and likely causes
4. Recommended actions for the operations team
5. Data pipeline health status

Format as a clean Markdown report.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.3,
    )
    return response.choices[0].message.content


def chat_with_energy_data(user_message: str, chat_history: list) -> str:
    """
    Send user message to Groq LLaMA 3 with energy data context injected.
    Chat history maintains conversation continuity.
    """
    client = get_groq_client()
    context = build_energy_context()

    system_prompt = f"""
You are EnergyOps AI — an intelligent assistant for monitoring energy consumption
across global manufacturing sites. You help operations engineers understand
energy patterns, investigate anomalies, and optimise consumption.

{context}

Be concise, data-driven, and actionable. Always reference specific numbers
when available. If you detect concerning patterns, flag them proactively.
"""
    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history[-6:]:
        messages.append(msg)
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=500,
        temperature=0.5,
    )
    return response.choices[0].message.content
