# src/agents/planner_agent.py (DEFINITIVE FIX - Focus on Part Construction)
import os
import json
from typing import List, Dict, Any
from langdetect import detect, lang_detect_exception
from pydantic import BaseModel, Field
from google import genai
from google.genai.types import GenerateContentConfig, Part

# --- Pydantic Schema is Unchanged ---
class DecomposedPlan(BaseModel):
    """A structured plan containing the original query, detected language, and sub-queries."""
    original_query: str = Field(description="The user's original, complex query.")
    detected_language: str = Field(description="The ISO 639-1 code of the detected query language (e.g., 'en', 'de').")
    sub_queries: List[str] = Field(description="A list of simpler, decomposed questions that must be answered to solve the original query. Generate a MINIMUM of three distinct, multi-hop sub-queries.")

# --- Planner Agent Implementation ---
class PlannerAgent:
    def __init__(self, llm_model: str = "gemini-2.5-flash"):
        self.llm_model = llm_model
        
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                 raise ValueError("GEMINI_API_KEY environment variable not set.")

            self.client = genai.Client(api_key=api_key)
            self.response_schema = DecomposedPlan.model_json_schema()
            
            print(f"PlannerAgent initialized with model: {self.llm_model} (Gemini)")
        except Exception as e:
            print(f"WARNING: Gemini client failed to initialize: {e}.")
            self.client = None

    def detect_language(self, query: str) -> str:
        """Detects the language of the query using langdetect."""
        try:
            return detect(query)
        except lang_detect_exception.LangDetectException:
            return 'unknown'
            
    def decompose_query(self, query: str) -> DecomposedPlan:
        """
        Uses Gemini LLM with structured output to decompose the query.
        """
        detected_lang = self.detect_language(query)
        print(f"Detected language: {detected_lang}")
        
        if self.client is None:
             return DecomposedPlan(original_query=query, detected_language=detected_lang, sub_queries=[query])

        # 1. Define the decomposition system instruction
        system_instruction = f"""
        You are an expert Policy Research Planner. Your task is to analyze a complex, multi-step user query and decompose it into a set of simpler, independent, atomic retrieval questions.

        **DECOMPOSITION RULE:** The query requires **multi-hop reasoning** to synthesize a final answer. You MUST generate a MINIMUM of three distinct sub-queries, covering all conceptual components: 'innovation', 'employment protection', and 'health equity'.
        
        The final output MUST be a JSON object that strictly adheres to the provided schema. Do not include any explanations or extra text outside the JSON object.
        """

        # 2. Configure the content generation for structured output (JSON Mode)
        config = GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=self.response_schema,
            temperature=0.1
        )

        # 3. Call the Gemini API
        try:
            # DEFINITIVE FIX: Build the complete prompt string and use direct object construction
            user_prompt_content = (
                "Please decompose the following complex query into the required structured JSON format. "
                "The query is: " + query
            )
            
            response = self.client.models.generate_content(
                model=self.llm_model,
                contents=[
                    # Use the Part object constructor with the 'text' keyword argument
                    # This avoids the class method 'from_text' that is causing the error.
                    Part(text=user_prompt_content) 
                ],
                config=config,
            )
            
            # 4. Parse the raw JSON string into the Pydantic object
            json_string = response.text
            plan = DecomposedPlan.model_validate_json(json_string) 
            
            plan.detected_language = detected_lang 
            return plan

        except Exception as e:
            print(f"LLM Decomposition failed (Gemini API Error: {e}). Falling back to simple query.")
            return DecomposedPlan(original_query=query, detected_language=detected_lang, sub_queries=[query])

    def route_and_plan(self, query: str) -> Dict[str, Any]:
        """
        Executes language detection and query decomposition, returning a dict.
        """
        plan_pydantic = self.decompose_query(query)
        plan_dict = plan_pydantic.model_dump() 
        return plan_dict