# src/agents/guardrails_agent.py (CONSOLIDATED)
import re
import spacy
from typing import List, Dict, Any, Tuple

class GuardrailsAgent:
    """
    Performs PII redaction and detects prompt injection attempts.
    """
    def __init__(self):
        try:
            self.nlp_ner = spacy.load("en_core_web_sm")
        except:
            self.nlp_ner = None
            print("WARNING: spaCy model not loaded. NER-based PII redaction disabled.")
            
        self.injection_keywords = r'(ignore the above|act as|forget everything|jailbreak|now generate)'

    def redact_pii(self, text: str) -> str:
        """Redacts common PII types using regex and spaCy NER."""
        
        redacted_text = text
        
        # 1. Regex Redaction (Emails, Phone Numbers)
        redacted_text = re.sub(r'[\w\.-]+@[\w\.-]+', '[REDACTED_EMAIL]', redacted_text)
        redacted_text = re.sub(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '[REDACTED_PHONE]', redacted_text)
        
        # 2. NER-based Redaction (Names, Locations)
        if self.nlp_ner:
            doc = self.nlp_ner(redacted_text)
            pii_labels = ["PERSON", "NORP", "ORG", "GPE"] 
            
            for ent in doc.ents:
                if ent.label_ in pii_labels:
                    redacted_text = redacted_text.replace(ent.text, f"[REDACTED_{ent.label_}]")
                    
        return redacted_text

    def detect_injection(self, query: str) -> bool:
        """Detects simple keyword-based prompt injection attempts."""
        if re.search(self.injection_keywords, query, re.IGNORECASE):
            return True
            
        return False

    def process_guardrails(self, user_input: str, generated_output: str) -> Dict[str, Any]:
        """Runs all guardrail checks."""
        
        # Placeholder PII for injection testing purposes
        output_with_pii_injection = generated_output.replace("Jane Smith", "John Doe (john.doe@example.com)") 
        
        injection_detected = self.detect_injection(user_input)
        
        if injection_detected:
            return {
                "input_status": "INJECTION_ATTEMPT_DETECTED",
                "redacted_output": "[GUARDRAIL FAILED: PROMPT INJECTION DETECTED]",
                "injection_check": True
            }
        
        redacted_output = self.redact_pii(output_with_pii_injection)
        
        return {
            "input_status": "OK",
            "redacted_output": redacted_output,
            "injection_check": False
        }