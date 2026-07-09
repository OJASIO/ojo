import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Any

class EmbeddingAgent:
    """Builds TF-IDF (sparse) and SBERT (dense) representations."""
    def __init__(self, sbert_model_name: str = 'all-MiniLM-L6-v2'):
        # 1. SBERT Model (Transformer Embeddings)
        print(f"Loading SBERT model: {sbert_model_name}")
        self.sbert_model = SentenceTransformer(sbert_model_name)
        
        # 2. TF-IDF for Classical Representation
        self.tfidf_vectorizer = TfidfVectorizer()

    def _prepare_content(self, processed_chunks: List[Dict[str, Any]]) -> List[str]:
        """Extracts the raw content for sentence embedding."""
        return [chunk['content'] for chunk in processed_chunks]

    def build_embeddings(self, processed_chunks: List[Dict[str, Any]]) -> Dict[str, np.ndarray]:
        """Generates all specified embedding types."""
        documents = self._prepare_content(processed_chunks)

        # A. SBERT Embeddings (Dense)
        print("Generating SBERT embeddings...")
        sbert_embeddings = self.sbert_model.encode(documents, convert_to_numpy=True)
        print(f"SBERT shape: {sbert_embeddings.shape}")
        
        # B. TF-IDF Embeddings (Sparse/Bag-of-Words)
        print("Generating TF-IDF embeddings (for visualization comparison)...")
        # Note: We fit/transform here using the raw content, similar to the Topic Agent's process
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
        tfidf_embeddings = tfidf_matrix.toarray()
        print(f"TF-IDF shape: {tfidf_embeddings.shape}")
        
        # For the purpose of Hybrid RAG (Task 3), the vectorizer itself is often needed, 
        # but for Task 2 (diagnostics), the dense array is what we plot.

        return {
            "sbert": sbert_embeddings,
            "tfidf": tfidf_embeddings,
        }