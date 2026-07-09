# src/agents/evaluator_agent.py

import json
from typing import List, Dict, Any, Optional
from ollama import Client as OllamaClient
from ollama import ResponseError


class EvaluatorAgent:
    """
    LLM-as-Judge evaluator for RAG pipeline outputs.
    Scores answers on Faithfulness, Relevancy,
    Context Precision, and Completeness.
    """

    def __init__(
        self,
        llm_model: str = "mistral:7b",
        ollama_host: str = "http://localhost:11434"
    ):
        self.llm_model = llm_model
        try:
            self.client = OllamaClient(host=ollama_host)
            self.client.show(self.llm_model)
            print(f"EvaluatorAgent initialized with local Ollama model: {self.llm_model} at {ollama_host}")
            self.evaluation_history = []
        except Exception as e:
            print(f"ERROR: Ollama client failed for EvaluatorAgent: {e}")
            print(f"ACTION: Ensure Ollama desktop app is running and '{self.llm_model}' is pulled.")
            self.client = None
            self.evaluation_history = []

    # ------------------------------------------------------------------
    # Private helper — called by every judge method
    # ------------------------------------------------------------------

    def _call_llm_json(self, prompt: str) -> dict:
        """
        Sends a prompt to the LLM and returns a parsed JSON dict.
        Handles markdown code fences that LLMs sometimes wrap around JSON.
        """
        if self.client is None:
            return {"score": 1, "reasoning": "LLM unavailable"}

        try:
            response = self.client.chat(
                model=self.llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert evaluator. "
                            "Always respond in valid JSON only. "
                            "Never include markdown formatting or code fences."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={"temperature": 0.1}
            )

            raw_text = response["message"]["content"].strip()

            # Strip markdown fences if present: ```json ... ```
            if "```" in raw_text:
                parts = raw_text.split("```")
                # parts[1] contains the fenced content
                raw_text = parts[1]
                # Remove language tag e.g. "json\n"
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]

            return json.loads(raw_text.strip())

        except ResponseError as e:
            return {"score": 1, "reasoning": f"Ollama error: {e}"}
        except json.JSONDecodeError:
            return {"score": 1, "reasoning": "JSON parse failed — LLM returned non-JSON"}
        except Exception as e:
            return {"score": 1, "reasoning": f"Unexpected error: {e}"}

    # ------------------------------------------------------------------
    # The 4 Judges
    # ------------------------------------------------------------------

    def judge_faithfulness(
        self,
        answer: str,
        context: str
    ) -> Dict[str, Any]:
        """
        Is every claim in the answer supported by the retrieved context?
        Catches hallucinations.
        Score 1-5:
          5 = every claim directly supported by context
          3 = some claims supported, some not
          1 = answer contradicts or ignores context
        """
        prompt = f"""You are evaluating whether an AI-generated answer is faithful to its source context.

RETRIEVED CONTEXT:
{context}

GENERATED ANSWER:
{answer}

TASK:
1. Break the answer into individual claims.
2. Check each claim against the context.
3. Score faithfulness 1-5:
   - 5: Every claim is directly supported by the context
   - 4: Most claims supported, very minor unsupported details
   - 3: Some claims supported, some not verifiable
   - 2: Few claims supported, mostly unsupported
   - 1: Answer contradicts or ignores the context entirely

Respond ONLY in this JSON format:
{{
    "score": <integer 1-5>,
    "reasoning": "<one sentence explanation>"
}}"""

        result = self._call_llm_json(prompt)
        return {
            "score": float(result.get("score", 1)),
            "reasoning": result.get("reasoning", "No reasoning provided")
        }

    def judge_relevancy(
        self,
        question: str,
        answer: str
    ) -> Dict[str, Any]:
        """
        Does the answer actually address the question asked?
        Score 1-5:
          5 = directly and completely answers the question
          3 = partially addresses the question
          1 = does not address the question at all
        """
        prompt = f"""You are evaluating whether an AI-generated answer is relevant to the question.

QUESTION:
{question}

GENERATED ANSWER:
{answer}

TASK:
Score how well the answer addresses the question 1-5:
- 5: Answer directly and completely addresses the question
- 4: Answer mostly addresses the question with minor gaps
- 3: Answer partially addresses the question
- 2: Answer is tangentially related but misses the core question
- 1: Answer does not address the question at all

Respond ONLY in this JSON format:
{{
    "score": <integer 1-5>,
    "reasoning": "<one sentence explanation>"
}}"""

        result = self._call_llm_json(prompt)
        return {
            "score": float(result.get("score", 1)),
            "reasoning": result.get("reasoning", "No reasoning provided")
        }

    def judge_context_precision(
        self,
        question: str,
        context: str
    ) -> Dict[str, Any]:
        """
        Were the retrieved chunks actually useful for answering the question?
        This evaluates RETRIEVAL quality, not generation quality.
        Score 1-5:
          5 = all retrieved context is highly relevant to the question
          3 = mixed — roughly half relevant, half noise
          1 = retrieved context has nothing to do with the question
        """
        prompt = f"""You are evaluating the quality of retrieved context for answering a question.

QUESTION:
{question}

RETRIEVED CONTEXT:
{context}

TASK:
Evaluate how relevant the retrieved context is for answering the question.
Score 1-5:
- 5: All retrieved context is highly relevant to the question
- 4: Most context relevant, one or two off-topic sections
- 3: Mixed — roughly half relevant, half noise
- 2: Mostly irrelevant context retrieved
- 1: Retrieved context has nothing to do with the question

Respond ONLY in this JSON format:
{{
    "score": <integer 1-5>,
    "reasoning": "<one sentence explanation>"
}}"""

        result = self._call_llm_json(prompt)
        return {
            "score": float(result.get("score", 1)),
            "reasoning": result.get("reasoning", "No reasoning provided")
        }

    def judge_completeness(
        self,
        question: str,
        answer: str,
        context: str
    ) -> Dict[str, Any]:
        """
        Did the answer use all relevant information available in the context?
        Score 1-5:
          5 = answer is comprehensive, covers all key points in context
          3 = answer covers some key points but misses important ones
          1 = answer ignores most available relevant information
        """
        prompt = f"""You are evaluating whether an AI-generated answer is complete given the available context.

QUESTION:
{question}

RETRIEVED CONTEXT:
{context}

GENERATED ANSWER:
{answer}

TASK:
Check if the answer covers all important information from the context
that is relevant to the question.
Score 1-5:
- 5: Answer is comprehensive, covers all key points from context
- 4: Answer covers most key points, minor omissions
- 3: Answer covers some key points but misses important ones
- 2: Answer is superficial, misses most key information
- 1: Answer ignores available relevant information entirely

Respond ONLY in this JSON format:
{{
    "score": <integer 1-5>,
    "reasoning": "<one sentence explanation>"
}}"""

        result = self._call_llm_json(prompt)
        return {
            "score": float(result.get("score", 1)),
            "reasoning": result.get("reasoning", "No reasoning provided")
        }

    # ------------------------------------------------------------------
    # Main evaluate method — runs all 4 judges
    # ------------------------------------------------------------------

    def evaluate(
        self,
        question: str,
        answer: str,
        retrieved_contexts: List[str],
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Main evaluation method. Runs all 4 judges and returns
        structured scores with verdict.

        Args:
            question: The original user query
            answer: The generated answer to evaluate
            retrieved_contexts: List of retrieved text chunks
            language: "en" or "de"

        Returns:
            Full evaluation result dict with scores, reasoning, and verdict
        """
        if not answer or not question:
            return {"error": "Missing question or answer"}

        # Join contexts into one string for judges
        context_str = "\n\n---\n\n".join(retrieved_contexts) if retrieved_contexts else "No context retrieved."

        print(f"EvaluatorAgent: Running 4 judges for query: '{question[:60]}...'")

        # Run all 4 judges
        faithfulness = self.judge_faithfulness(answer, context_str)
        relevancy = self.judge_relevancy(question, answer)
        context_precision = self.judge_context_precision(question, context_str)
        completeness = self.judge_completeness(question, answer, context_str)

        # Calculate overall score
        scores = {
            "faithfulness": faithfulness["score"],
            "relevancy": relevancy["score"],
            "context_precision": context_precision["score"],
            "completeness": completeness["score"]
        }
        overall_score = round(sum(scores.values()) / len(scores), 2)

        # Assign verdict
        if overall_score >= 4.5:
            verdict = "EXCELLENT"
        elif overall_score >= 3.5:
            verdict = "GOOD"
        elif overall_score >= 2.5:
            verdict = "ACCEPTABLE"
        elif overall_score >= 1.5:
            verdict = "POOR"
        else:
            verdict = "FAILED"

        result = {
            "question": question,
            "answer": answer[:200] + "..." if len(answer) > 200 else answer,
            "language": language,
            "scores": scores,
            "reasoning": {
                "faithfulness": faithfulness["reasoning"],
                "relevancy": relevancy["reasoning"],
                "context_precision": context_precision["reasoning"],
                "completeness": completeness["reasoning"]
            },
            "overall_score": overall_score,
            "verdict": verdict
        }

        # Store in history for aggregate metrics
        self.evaluation_history.append(result)

        print(f"EvaluatorAgent: Overall Score = {overall_score}/5 | Verdict = {verdict}")
        return result

    # ------------------------------------------------------------------
    # Aggregate metrics across multiple evaluations
    # ------------------------------------------------------------------

    def get_aggregate_metrics(self) -> Dict[str, Any]:
        """
        Returns aggregate metrics across all evaluations run so far.
        Useful for measuring overall pipeline quality.
        Put these numbers in your README.
        """
        if not self.evaluation_history:
            return {"error": "No evaluations run yet"}

        criteria = ["faithfulness", "relevancy", "context_precision", "completeness"]
        aggregates = {}

        for criterion in criteria:
            scores = [
                e["scores"][criterion]
                for e in self.evaluation_history
                if criterion in e.get("scores", {})
            ]
            if scores:
                aggregates[criterion] = {
                    "mean": round(sum(scores) / len(scores), 3),
                    "min": round(min(scores), 3),
                    "max": round(max(scores), 3)
                }

        overall_scores = [
            e["overall_score"]
            for e in self.evaluation_history
            if "overall_score" in e
        ]

        aggregates["overall"] = {
            "mean": round(sum(overall_scores) / len(overall_scores), 3),
            "total_evaluations": len(self.evaluation_history)
        }

        # Verdict distribution
        verdicts = [e["verdict"] for e in self.evaluation_history if "verdict" in e]
        aggregates["verdict_distribution"] = {
            v: verdicts.count(v) for v in set(verdicts)
        }

        return aggregates
