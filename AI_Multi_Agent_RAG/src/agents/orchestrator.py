# main_orchestrator.py
import subprocess
import os
import sys
import time
from typing import List, Tuple

# --- Configuration ---
# Define the sequence of tasks to run. Task 7 and 8 run last for final analysis.
TASK_SCRIPTS: List[Tuple[str, str]] = [
    ("Task 1: PDF Ingestion & Pre-Processing", "run_task_1.py"),
    ("Task 2: Topic Modeling & Diagnostics", "run_task_2.py"),
    ("Task 3: Hybrid Retrieval Indexing (Pinecone)", "run_task_3.py"),
    ("Task 4: Planning & Query Decomposition", "run_task_4.py"),
    ("Task 5: Synthesis & Debate", "run_task_5.py"),
    ("Task 6: Verification & Guardrails", "run_task_6.py"),
    # Task 7 and 8 are analysis/adaptive steps, run after the full pipeline cycle
    ("Task 7: Adaptivity & Visualization", "run_task_7.py"),
    ("Task 8: Advanced Retrieval (GraphRAG)", "run_task_8_graph.py"),
]

def execute_task(name: str, script_path: str) -> bool:
    """Executes a single Python script using subprocess."""
    print(f"\n=======================================================")
    print(f"STARTING: {name}")
    print(f"=======================================================")
    
    # Use sys.executable to ensure we run with the correct Python interpreter (e.g., venv)
    command = [sys.executable, script_path]
    
    try:
        # Run the script and raise an error if the script fails
        process = subprocess.run(
            command,
            check=True,  
            capture_output=False,
            text=True
        )
        print(f"\nSUCCESS: {name} completed.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: {name} failed with exit code {e.returncode}.")
        print("-------------------- STDERR --------------------")
        print(e.stderr)
        print("\n[ADVICE]: Task 3 (Pinecone) failures are often due to external APIs. Check API keys and network. Proceeding with analysis stages.")
        return False
    except FileNotFoundError:
        print(f"\nERROR: Script file not found: {script_path}. Ensure it exists in the root directory.")
        return False
    
    # main_orchestrator.py (Continued)

def run_full_pipeline():
    """Runs the entire multi-agent RAG pipeline sequentially."""
    
    print("\n\n--- Multi-Agent RAG Pipeline Orchestrator ---")
    print("Executing adaptive RAG workflow across 8 stages.")
    start_time = time.time()
    
    # Check for critical files (simulating required setup)
    if not os.path.exists('data/pdfs'):
        print("\nCRITICAL WARNING: 'data/pdfs' directory not found. Please add PDF policy files to run Tasks 1-3.")
        
    all_success = True
    
    for name, script_path in TASK_SCRIPTS:
        success = execute_task(name, script_path)
        
        if not success:
            all_success = False
            # Allow Task 3 failure, but stop the pipeline on other critical failures (like Task 1/4/5)
            if name not in ["Task 3: Hybrid Retrieval Indexing (Pinecone)"]:
                print(f"\nCRITICAL FAILURE: Pipeline stopped due to {name} error.")
                return
        
        # If Task 3 failed, we still proceed because subsequent tasks (4-8) rely on simulated/local outputs.

    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n\n=======================================================")
    print("✨ PIPELINE EXECUTION COMPLETE ✨")
    print(f"Total Execution Time: {total_time:.2f} seconds")
    print("=======================================================")
    if not all_success:
        print("NOTE: Some tasks may have failed due to external API dependencies (Pinecone/LLM).")
    print("Check the 'results/' folder for final metrics and plots.")
    
if __name__ == "__main__":
    # Ensure all run_task_X.py files are present in the root directory
    run_full_pipeline()