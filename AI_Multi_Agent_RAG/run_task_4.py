# run_task_4.py
import os
import json
from src.agents.planner_agent import PlannerAgent
from src.utils import save_json
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
PLAN_OUTPUT_FILE = 'D:/NLP_Final_Project/Examination-master/results/plan.json'

# --- Test Query ---
# This is the single, complex query you want to decompose
COMPLEX_QUERY = "Compare fiscal strategies for financing climate and social protection goals across OECD, IMF, and UNCTAD documents. Identify points of convergence and divergence using multi-hop retrieval."

def transform_plan_to_desired_format(plan_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms the LLM output into the user's desired nested format:
    { "original_query": ..., "language": ..., "sub_queries": { query: [] } }
    """
    if not plan_dict or 'sub_queries' not in plan_dict:
        return {}

    # Transform the list of sub-queries into the dictionary format: {query: []}
    sub_queries_dict = {
        query: [] for query in plan_dict['sub_queries']
    }
    
    return {
        "original_query": plan_dict['original_query'],
        "language": plan_dict['detected_language'],
        "sub_queries": sub_queries_dict
    }

def run_task_4():
    """Executes the Planning and Multilingual Query Routing task."""
    print("--- Starting Task 4: Planning & Multilingual Query Routing ---")

    # ACTION REQUIRED: Check for the Gemini API Key
    if not os.getenv("GEMINI_API_KEY"):
         print("ERROR: GEMINI_API_KEY not set.")
         print("ACTION REQUIRED: Please set the GEMINI_API_KEY environment variable to use the PlannerAgent.")
         return

    planner_agent = PlannerAgent()
    
    print(f"\nProcessing Complex Query: '{COMPLEX_QUERY}'")
    
    # 1. Run the decomposition agent
    plan_output = planner_agent.route_and_plan(COMPLEX_QUERY)
    
    # 2. Transform the plan to the specific desired JSON structure
    final_output = transform_plan_to_desired_format(plan_output)

    # 3. Print and Save the result
    print(f"  -> Detected Language: {final_output.get('language')}")
    print(f"  -> Decomposed Sub-queries ({len(final_output.get('sub_queries', {}))}):")
    for sub_query in final_output.get('sub_queries', {}).keys():
        print(f"     - {sub_query}")

    save_json(final_output, PLAN_OUTPUT_FILE)
    
    print("\n--- Task 4 Completed Successfully ---")


if __name__ == "__main__":
    os.makedirs(os.path.dirname(PLAN_OUTPUT_FILE), exist_ok=True)
    run_task_4()