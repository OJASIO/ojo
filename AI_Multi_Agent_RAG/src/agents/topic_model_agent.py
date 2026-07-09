import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from typing import List, Dict, Any, Tuple

class TopicModelAgent:
    """Performs Topic Discovery using Non-negative Matrix Factorization (NMF)."""
    def __init__(self, n_topics: int = 10, max_df: float = 0.85, min_df: int = 2):
        self.n_topics = n_topics
        self.max_df = max_df
        self.min_df = min_df
        self.vectorizer = None
        self.nmf_model = None

    def _prepare_data(self, processed_chunks: List[Dict[str, Any]]) -> List[str]:
        """Extracts and joins lemmas for vectorization."""
        documents = []
        for chunk in processed_chunks:
            # Filter out tokens that are not useful for topic modeling (punctuation, spaces, etc.)
            lemmas = [
                token['lemma'] for token in chunk.get('tokens', []) 
                if token['pos'] not in ['PUNCT', 'SPACE', 'SYM', 'X']
            ]
            documents.append(" ".join(lemmas))
        return documents

    def train_topic_model(self, processed_chunks: List[Dict[str, Any]]) -> Tuple[List[str], np.ndarray]:
        """Trains NMF and returns dominant topics and the document-topic matrix."""
        print(f"Starting NMF Topic Modeling with {self.n_topics} topics...")
        documents = self._prepare_data(processed_chunks)
        
        # 1. Build TF-IDF Matrix (Feature Representation)
        self.vectorizer = TfidfVectorizer(
            max_df=self.max_df, 
            min_df=self.min_df, 
            stop_words='english',
            ngram_range=(1, 2) # Include bigrams for better topic coherence
        )
        tfidf_matrix = self.vectorizer.fit_transform(documents)
        feature_names = self.vectorizer.get_feature_names_out()
        print(f"TF-IDF Matrix shape: {tfidf_matrix.shape}")

        # 2. Train NMF Model
        self.nmf_model = NMF(
            n_components=self.n_topics, 
            random_state=42, # Ensure reproducibility
            max_iter=300, 
            solver='mu'
        ).fit(tfidf_matrix)

        # 3. Extract Topics
        topic_descriptions = self._get_topics(feature_names)
        
        # 4. Get Document-Topic Matrix (W matrix: Chunk-Topic weights)
        doc_topic_matrix = self.nmf_model.transform(tfidf_matrix)

        return topic_descriptions, doc_topic_matrix

    def _get_topics(self, feature_names: np.ndarray, n_top_words: int = 10) -> List[str]:
        """Returns a list of descriptive strings for each topic."""
        topics = []
        for topic_idx, topic in enumerate(self.nmf_model.components_):
            top_features_ind = topic.argsort()[:-n_top_words - 1:-1]
            top_features = [feature_names[i] for i in top_features_ind]
            topics.append(f"Topic {topic_idx}: {' / '.join(top_features)}")
        return topics