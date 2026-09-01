import json
import os
from dotenv import load_dotenv
from google import genai
from backend.prompts import get_prompt

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=api_key)

def review_cv(cv_text: str, lang: str) -> dict:
    prompt = get_prompt(lang).format(cv_text=cv_text)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    raw = response.text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print(f"JSON parse failed. Raw response:\n{raw[:300]}")
        return {
            "overall_score": 0,
            "tier_1": [],
            "tier_2": [],
            "tier_3": [],
            "summary": "Analysis could not be completed. Please try again.",
            "ready": False,
        }