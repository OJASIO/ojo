# run_task_7.py
import os
import json
import time
from src.agents.memory_agent import MemoryAgent, MEMORY_FILE
from src.agents.visualizer_agent import VisualizerAgent
from src.utils import save_json
from typing import Dict, Any

# --- Configuration ---
METRICS_INPUT_FILE = 'results/metrics.json'
RETRIEVAL_PARAMS_FILE = 'results/retrieval_params.json' # File to save updated params

def load_metrics() -> Dict[str, Any]:
    """Loads the metrics output from the completed Task 6 run."""
    if os.path.exists(METRICS_INPUT_FILE):
        with open(METRICS_INPUT_FILE, 'r') as f:
            return json.load(f)
    print(f"ERROR: Task 6 metrics file not found at {METRICS_INPUT_FILE}. Cannot log run.")
    # Return sensible defaults for the memory agent to log a failing run
    return {
        "guardrail_status": "OK",
        "verifier_metrics": {
            "total_statements_checked": 1, 
            "factually_entailed_count": 0, 
            "statement_checks": []
        }
    }

def run_task_7():
    """
    Executes the Memory and Visualization task, simulating the adaptive loop.
    """
    print("--- Starting Task 7: Adaptivity & Visualization ---")
    start_time = time.time()

    # 1. Initialize Agents
    memory_agent = MemoryAgent()
    visualizer_agent = VisualizerAgent()

    # 2. Log the results of the immediately preceding Task 6 run
    task_6_metrics = load_metrics()
    end_time = time.time()
    
    # Placeholder for current retrieval parameters (should come from a prior Task 3 run)
    # We use the defaults stored in memory for the first run
    current_params = memory_agent.memory['retrieval_params']
    
    print("\n2. Logging current run metrics to memory...")
    memory_agent.log_run_metrics(
        retrieval_params=current_params,
        metrics=task_6_metrics,
        latency=(end_time - start_time)
    )

    # 3. Auto-Tune the Pipeline (Determine next alpha and k)
    print("\n3. Auto-Tuning Retrieval Parameters...")
    new_alpha, new_k = memory_agent.auto_tune_retrieval()
    
    print(f"   -> NEW Hybrid RAG Parameters calculated: Alpha={new_alpha:.2f}, K={new_k}")

    # 4. Save the new parameters (The Orchestrator would use this file for the next run)
    save_json({"alpha": new_alpha, "k": new_k}, RETRIEVAL_PARAMS_FILE)
    print(f"   -> New retrieval parameters saved to {RETRIEVAL_PARAMS_FILE}")

    # 5. Generate Visualizations
    print("\n4. Generating Visualizations...")
    
    plot_path_confidence = visualizer_agent.plot_confidence_trajectory(memory_agent.memory['history'])
    plot_path_graph = visualizer_agent.plot_agent_graph()
    
    print(f"   -> Confidence Plot saved to {plot_path_confidence}")
    print(f"   -> Agent Graph saved to {plot_path_graph}")

    print("\n--- Task 7 Completed Successfully ---")


if __name__ == "__main__":
    os.makedirs('results/plots', exist_ok=True)
    run_task_7()