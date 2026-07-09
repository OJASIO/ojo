# src/agents/debate_agents.py (OLLAMA CLIENT WITH ENDPOINT)
import os
from typing import Dict, Any, List
from ollama import Client as OllamaClient
from ollama import ResponseError

class DebateAgents:
    """
    Simulates a debate between two agents with opposing views to achieve consensus 
    using the local Ollama inference engine.
    """
    def __init__(self, llm_model: str = "mistral:7b", ollama_host: str = "http://localhost:11434"):
        self.llm_model = llm_model
        try:
            # Explicitly set the host endpoint
            self.client = OllamaClient(host=ollama_host)
            self.client.show(self.llm_model)
            print(f"DebateAgents initialized with local Ollama model: {self.llm_model} at {ollama_host}")
        except Exception as e:
            print(f"ERROR: Ollama client failed for DebateAgents: {e}")
            self.client = None

    def _safe_generate(self, messages: List[Dict[str, str]], temperature: float) -> str:
        """Handles Ollama API call."""
        if self.client is None:
            raise ConnectionError("Ollama client is not initialized.")
            
        try:
            response = self.client.chat(
                model=self.llm_model,
                messages=messages,
                options={'temperature': temperature}
            )
            return response['message']['content']
        except ResponseError as e:
            return f"LLM Debate Step Failed: Ollama Error - {e}"
        except Exception as e:
            return f"LLM Debate Step Failed: General Error - {e}"

    def _debate_step(self, summary: str, perspective: str, role: str) -> str:
        """Helper to get a critique from a specific agent perspective."""
        system_prompt = f"You are a policy critique agent focused on the {perspective} perspective. Argue strongly for your side. You are {role}."
        user_prompt = f"""
        **Preliminary Policy Synthesis to Critique:**
        {summary}
        
        **Critique Task:**
        1. Identify weaknesses in the current policy balance (e.g., if it favors innovation too much, argue for more protection).
        2. Propose 1-2 concrete revisions to strengthen the policy's balance based on your {perspective} role.
        
        **Critique and Proposed Revisions (Keep citations intact where relevant):**
        """
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
        
        return self._safe_generate(messages, temperature=0.7)

    def run_debate(self, summary: str) -> str:
        """Runs the 3-step debate process: Critique A, Critique B, Consensus."""
        if self.client is None:
            return "ERROR: LLM client failed to initialize. Cannot run debate."

        # 1. Agent A Critique 
        role_a = "Agent A (The Protectionist)"
        critique_a = self._debate_step(summary, "Employment Protection and Health Equity", role_a)
        print(f"\n--- {role_a} Critique Generated ---")

        # 2. Agent B Critique 
        role_b = "Agent B (The Innovator)"
        critique_b = self._debate_step(summary, "Technological Innovation and Economic Growth", role_b)
        print(f"--- {role_b} Critique Generated ---")
        
        # 3. Final Consensus Synthesis
        consensus_system_prompt = "You are the Final Consensus Arbitrator. Your task is to take the initial Synthesis and the two opposing Critiques, and produce a single, final, unified Policy Brief that resolves the conflicts and establishes a balanced framework."
        
        consensus_user_prompt = f"""
        **Initial Synthesis:** {summary}
        
        **Agent A Critique (Protectionist):** {critique_a}
        
        **Agent B Critique (Innovator):** {critique_b}
        
        **Task:**
        Produce the FINAL Policy Brief. It must be structured and directly address the original query's goal (AI-governance balancing innovation, employment, and health). All previous citations MUST be carried forward to the final brief.
        
        **FINAL Unified AI-Governance Framework Policy Brief:**
        """
        
        messages = [
            {'role': 'system', 'content': consensus_system_prompt},
            {'role': 'user', 'content': consensus_user_prompt}
        ]
        
        return self._safe_generate(messages, temperature=0.2)