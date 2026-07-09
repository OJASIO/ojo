# src/agents/preprocessor_agent.py
# Bilingual version — supports English and German

import spacy
from langdetect import detect, LangDetectException
from typing import List, Dict, Any


class PreprocessorAgent:
    """
    Performs tokenization, POS tagging, lemmatization, and NER.
    Supports English and German documents automatically.
    Uses language detection to select the correct spaCy model.

    Setup:
        python -m spacy download en_core_web_sm
        python -m spacy download de_core_news_sm
    """

    def __init__(self):
        # Load English model
        try:
            self.nlp_en = spacy.load("en_core_web_sm")
            print("PreprocessorAgent: English model (en_core_web_sm) loaded.")
        except OSError:
            print("ERROR: en_core_web_sm not found. Run: python -m spacy download en_core_web_sm")
            raise

        # Load German model
        try:
            self.nlp_de = spacy.load("de_core_news_sm")
            print("PreprocessorAgent: German model (de_core_news_sm) loaded.")
        except OSError:
            print("WARNING: de_core_news_sm not found. Run: python -m spacy download de_core_news_sm")
            print("WARNING: German text will fall back to English model.")
            self.nlp_de = None

    def _detect_language(self, text: str) -> str:
        """
        Detects language of a text chunk.
        Returns "de" for German, "en" for everything else.
        Falls back to "en" if detection fails.
        """
        try:
            # Only use first 500 chars for speed
            lang = detect(text[:500])
            return lang if lang in ["de", "en"] else "en"
        except LangDetectException:
            return "en"

    def _get_nlp(self, language: str):
        """
        Returns correct spaCy model for the detected language.
        Falls back to English if German model not available.
        """
        if language == "de" and self.nlp_de is not None:
            return self.nlp_de
        return self.nlp_en

    def process_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes a list of text chunks with the appropriate spaCy model.
        Automatically detects language per chunk.

        Args:
            chunks: List of chunk dicts with 'content' and 'metadata' keys

        Returns:
            List of processed chunk dicts with NLP annotations added
        """
        processed_data = []
        print(f"PreprocessorAgent: Processing {len(chunks)} chunks (bilingual EN/DE)...")

        en_count = 0
        de_count = 0

        for i, chunk in enumerate(chunks):
            content = chunk.get("content", "")

            # Detect language for this chunk
            language = self._detect_language(content)
            nlp = self._get_nlp(language)

            if language == "de":
                de_count += 1
            else:
                en_count += 1

            # Run spaCy pipeline
            doc = nlp(content)

            # 1. Tokenization, POS Tagging, Lemmatization
            tokens = [
                {
                    "text": token.text,
                    "lemma": token.lemma_,
                    "pos": token.pos_
                }
                for token in doc
                if not token.is_space
            ]

            # 2. Named Entity Recognition
            entities = [
                {
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                }
                for ent in doc.ents
            ]

            # 3. Extract entity types as metadata for filtering
            entity_map = {}
            for ent in doc.ents:
                label = ent.label_
                if label not in entity_map:
                    entity_map[label] = []
                if ent.text not in entity_map[label]:
                    entity_map[label].append(ent.text)

            processed_chunk = {
                "chunk_id": chunk.get("chunk_id", f"chunk_{i}"),
                "content": content,
                "metadata": chunk.get("metadata", {}),
                "language": language,
                "tokens": tokens,
                "named_entities": entities,
                "entity_map": entity_map,  # e.g. {"ORG": ["IMF", "OECD"], "DATE": ["2023"]}
            }

            processed_data.append(processed_chunk)

            if (i + 1) % 100 == 0:
                print(f"PreprocessorAgent: Processed {i + 1}/{len(chunks)} chunks...")

        print(f"PreprocessorAgent: Done. English chunks: {en_count}, German chunks: {de_count}")
        return processed_data
