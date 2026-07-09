# src/agents/summarizer_agent.py (OLLAMA CLIENT WITH ENDPOINT)
import os
from typing import List, Dict, Any
from ollama import Client as OllamaClient
from ollama import ResponseError

class SummarizerAgent:
    """
    Generates a structured summary with citations from retrieved context 
    using the local Ollama inference engine.
    """
    def __init__(self, llm_model: str = "mistral:7b", ollama_host: str = "http://localhost:11434"):
        self.llm_model = llm_model
        try:
            # Explicitly set the host endpoint
            self.client = OllamaClient(host=ollama_host)
            # Verify model is available
            self.client.show(self.llm_model)
            print(f"SummarizerAgent initialized with local Ollama model: {self.llm_model} at {ollama_host}")
        except Exception as e:
            print(f"ERROR: Ollama client failed for SummarizerAgent: {e}")
            print(f"ACTION: Ensure Ollama desktop app is running and '{self.llm_model}' is pulled.")
            self.client = None
            
    def synthesize_summary(self, plan: Dict[str, Any], retrieved_context: List[Dict[str, Any]]) -> str:
        """
        Synthesizes a policy summary based on the plan and retrieved context, ensuring citations.
        """
        if self.client is None:
            return "ERROR: LLM client failed to initialize. Cannot summarize."

        # 1. Format the context for the prompt (logic unchanged)
        context_string = ""
        if not retrieved_context:
            context_string = "No context was retrieved. The agent must rely on its internal knowledge."
        else:
            for i, doc in enumerate(retrieved_context):
                source_tag = f"[src: {doc.get('source', 'FILE')} p.{doc.get('page', 'X')}]"
                context_string += f"--- DOCUMENT {i+1} {source_tag} ---\n{doc.get('text', 'No text.')}\n\n"
        
        sub_queries_list = [f'- {q}' for q in plan.get('sub_queries', {}).keys()]
        
        # 2. Define the prompt using a single system + user structure
        system_prompt = "You are a highly analytical Policy Analyst. Your task is to synthesize the provided context snippets to create a preliminary policy report. You MUST use citations. Every piece of factual information (a sentence or a key phrase) MUST be immediately followed by its citation tag, e.g., 'AI regulations are currently fragmented [src: IMF_Report.pdf p.4].' If context is missing, do not cite that statement."
        
        user_prompt = f"""
        **User Query (Goal):** {plan.get('original_query', 'N/A')}
        
        **Decomposed Sub-queries (Evidence Goals):**
        {chr(10).join(sub_queries_list)}
        
        **Retrieved Context (Evidence):**
        {context_string}
        
        **Task:** Produce a well-structured summary (using bullet points and headings) that integrates the findings from the evidence to address the query's components (innovation, employment protection, health equity).
        
        **Preliminary Policy Synthesis:**
        """

        # 3. Call the Ollama LLM
        try:
            response = self.client.chat(
                model=self.llm_model,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                options={'temperature': 0.3}
            )
            return response['message']['content']
        except ResponseError as e:
            return f"LLM Summary Generation Failed: Ollama Error - {e}"
        except Exception as e:
            return f"LLM Summary Generation Failed: General Error - {e}"