# src/agents/memory_agent.py (CONSOLIDATED)
import json
import os
import time
from typing import Dict, Any, Tuple

# Configuration for the memory file
MEMORY_FILE = 'results/agent_memory.json'

class MemoryAgent:
    """
    Manages persistence of pipeline parameters and implements auto-tuning logic 
    based on verification metrics.
    """
    def __init__(self, memory_file: str = MEMORY_FILE):
        self.memory_file = memory_file
        self.memory = self._load_memory()
        
    def _load_memory(self) -> Dict[str, Any]:
        """Loads memory from the JSON file or initializes defaults."""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        
        # Default starting state for memory
        return {
            "retrieval_params": {"alpha": 0.5, "k": 5},
            "history": []
        }

    def save_memory(self):
        """Saves the current memory state to the JSON file."""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=4)
        print(f"MemoryAgent: Saved state to {self.memory_file}")

    def log_run_metrics(self, retrieval_params: Dict[str, float], metrics: Dict[str, Any], latency: float):
        """Logs the results of a complete pipeline run."""
        run_data = {
            "timestamp": time.time(),
            "retrieval_params": retrieval_params,
            "metrics": {
                "factually_entailed_count": metrics['verifier_metrics']['factually_entailed_count'],
                "total_statements_checked": metrics['verifier_metrics']['total_statements_checked'],
                "entailment_rate": metrics['verifier_metrics']['factually_entailed_count'] / metrics['verifier_metrics']['total_statements_checked'] if metrics['verifier_metrics']['total_statements_checked'] else 0,
                "guardrail_status": metrics['guardrail_status']
            },
            "latency_s": latency
        }
        self.memory['history'].append(run_data)
        self.save_memory()

    def auto_tune_retrieval(self) -> Tuple[float, int]:
        """
        Auto-tunes the Hybrid RAG parameters (alpha, k) based on recent factual precision.
        Optimization Goal: Maximize Entailment Rate.
        """
        if not self.memory['history']:
            return self.memory['retrieval_params']['alpha'], self.memory['retrieval_params']['k']

        # Get the last successful run's metrics
        last_run = self.memory['history'][-1]
        entailment_rate = last_run['metrics']['entailment_rate']
        current_alpha = last_run['retrieval_params']['alpha']
        current_k = last_run['retrieval_params']['k']
        
        new_alpha = current_alpha
        new_k = current_k
        
        print(f"MemoryAgent: Last Entailment Rate was {entailment_rate:.2f}.")

        # Simple Adaptive Logic: Adjust Alpha based on performance
        if entailment_rate < 0.5:
            # Performance is poor: Try shifting alpha slightly to explore new balance
            if current_alpha > 0.5:
                new_alpha = max(0.1, current_alpha - 0.2)
            # If closer to 0.0 (sparse), try moving towards dense (Semantic)
            else:
                new_alpha = min(0.9, current_alpha + 0.2)
            
            print(f"MemoryAgent: Low entailment rate. Adjusting alpha to {new_alpha:.2f}.")

        elif entailment_rate > 0.9:
            # Performance is very good: Increase k (retrieved documents) slightly to ensure coverage
            new_k = min(15, current_k + 1)
            print(f"MemoryAgent: High entailment rate. Increasing k to {new_k}.")

        # Update and save the new parameters
        self.memory['retrieval_params']['alpha'] = new_alpha
        self.memory['retrieval_params']['k'] = new_k
        self.save_memory()

        return new_alpha, new_k