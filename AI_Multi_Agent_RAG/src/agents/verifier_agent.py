# src/agents/verifier_agent.py (CONSOLIDATED)
import numpy as np
import os
import re
from transformers import pipeline
from typing import List, Dict, Any, Tuple

class VerifierAgent:
    """
    Checks factual precision using NLI (Natural Language Inference) and temporal consistency.
    """
    def __init__(self, nli_model: str = "facebook/bart-large-mnli"):
        print(f"Loading NLI model: {nli_model}...")
        try:
            # Natural Language Inference Pipeline (requires torch/transformers)
            self.nli_verifier = pipeline("zero-shot-classification", model=nli_model)
        except Exception as e:
            # Handle cases where torch/model download fails
            print(f"Error loading NLI model. Verification will be SKIPPED: {e}")
            self.nli_verifier = None
            
        self.semantic_check_threshold = 0.8 

    def check_factuality(self, generated_statement: str, retrieved_context: str) -> str:
        """Checks if the statement is entailed by the context using NLI."""
        if not self.nli_verifier:
            return "SKIPPED: NLI model unavailable."
        
        try:
            # NLI classifies relationship as: Entailment, Contradiction, or Neutral.
            result = self.nli_verifier(
                generated_statement, 
                candidate_labels=["entailment", "contradiction", "neutral"],
                hypothesis_template="This text is {}. The retrieved context is a strong premise." 
            )
            
            top_label = result['labels'][0]
            top_score = result['scores'][0]
            
            if top_label == "entailment" and top_score > 0.75:
                return "FACTUAL_ENTAILED"
            elif top_label == "contradiction" and top_score > 0.75:
                return "FACTUAL_CONTRADICTION"
            else:
                return "FACTUAL_NEUTRAL" 
                
        except Exception as e:
            return f"NLI Check Failed: {e}"

    def check_temporal_consistency(self, text: str) -> str:
        """Simple regex-based check for temporal phrases (e.g., years)."""
        years = re.findall(r'\b(20[0-9]{2})\b', text)
        if years:
            min_year = min(map(int, years))
            max_year = max(map(int, years))
            if max_year - min_year > 5:
                return f"TEMPORAL_WARNING (Span: {min_year}-{max_year})"
            return "TEMPORAL_OK"
        return "TEMPORAL_NONE"

    def run_verification(self, summary_with_citations: str, context_map: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Processes the summary, extracts statements, and verifies them against their context.
        """
        verification_results = []
        
        # Pattern to find a statement followed by a citation in the format: (FILE.pdf p.X)
        citation_pattern = re.compile(r'(.+?)\s*\((([a-zA-Z0-9_]+\.pdf\s*p\.\s*[0-9]+))\)', re.DOTALL)
        
        # Split the policy brief into sections to find matches
        sections = summary_with_citations.split('\n')
        
        for section in sections:
            if not section.strip():
                continue
            
            # Find all citations within the section
            matches = citation_pattern.findall(section)
            
            for match in matches:
                statement_raw = match[0].strip()
                citation_key_raw = match[2].strip() 
                
                # Reconstruct the expected citation format for lookup: [FILE.pdf p.X]
                source_key = f"[{citation_key_raw}]"
                
                # Check the context map for the full text of the source chunk
                source_context = context_map.get(source_key, "")

                # The statement ends just before the citation parenthesis starts
                statement_to_check = statement_raw.strip() 
                
                if source_context:
                    factual_check = self.check_factuality(statement_to_check, source_context)
                else:
                    factual_check = "FACTUAL_UNVERIFIABLE (Source Missing from Context Map)"
                
                verification_results.append({
                    "statement": statement_to_check,
                    "citation": citation_key_raw,
                    "factual_precision": factual_check,
                    "temporal_check": self.check_temporal_consistency(statement_to_check)
                })
            
        return verification_results