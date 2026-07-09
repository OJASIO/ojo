# src/agents/retriever_agent.py
# Updated with multilingual-e5-large for bilingual EN/DE retrieval

import os
import json
import numpy as np
from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from pinecone_text.sparse import BM25Encoder
from rank_bm25 import BM25Okapi
from dotenv import load_dotenv

load_dotenv()


class RetrieverAgent:
    """
    Implements Hybrid Retrieval (BM25 + Dense) using Pinecone.

    UPGRADE: Uses intfloat/multilingual-e5-large instead of all-MiniLM-L6-v2.
    This enables cross-lingual retrieval:
    - Query in English → retrieve German documents
    - Query in German → retrieve English documents
    - Dimension changes from 384 to 1024

    IMPORTANT: multilingual-e5-large requires prefixes:
    - Documents: "passage: " + text
    - Queries:   "query: " + text
    """

    def __init__(
        self,
        index_name: str,
        dimension: int = 1024,  # Changed from 384 to 1024 for e5-large
        sbert_model: str = "intfloat/multilingual-e5-large"  # Changed model
    ):
        # 1. Pinecone setup
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.environment = os.getenv("PINECONE_ENVIRONMENT")

        if not self.api_key or not self.environment:
            raise ValueError("PINECONE_API_KEY and PINECONE_ENVIRONMENT must be set in .env")

        self.pc = Pinecone(api_key=self.api_key)
        self.index_name = index_name
        self.dimension = dimension

        # 2. Dense Encoder — multilingual-e5-large
        print(f"Loading multilingual embedding model: {sbert_model}")
        print("Note: First run will download ~2.2GB model. This is a one-time download.")
        self.dense_encoder = SentenceTransformer(sbert_model)

        # 3. Sparse Encoder (BM25)
        self.sparse_encoder = BM25Encoder()

        self.index = self._initialize_pinecone_index()

    def _initialize_pinecone_index(self):
        """Creates the Pinecone index if it doesn't exist."""
        existing = [idx["name"] for idx in self.pc.list_indexes()]

        if self.index_name not in existing:
            print(f"Creating Pinecone index '{self.index_name}' with dimension {self.dimension}...")
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric="dotproduct",  # Required for sparse-dense hybrid search
                spec=ServerlessSpec(cloud="aws", region=self.environment)
            )
            print("Index created successfully.")

        return self.pc.Index(self.index_name)

    def _encode_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Encode documents with required 'passage: ' prefix.
        This is REQUIRED for multilingual-e5-large — without it, quality drops significantly.
        """
        prefixed = ["passage: " + text for text in texts]
        return self.dense_encoder.encode(prefixed, show_progress_bar=True).tolist()

    def _encode_query(self, query: str) -> List[float]:
        """
        Encode a query with required 'query: ' prefix.
        This is REQUIRED for multilingual-e5-large.
        Works for both English and German queries.
        """
        prefixed = "query: " + query
        return self.dense_encoder.encode(prefixed).tolist()

    def fit_sparse_encoder(self, corpus: List[str]):
        """Trains the BM25 encoder on the corpus."""
        print("Training BM25 Sparse Encoder...")
        self.sparse_encoder.fit(corpus)
        print("BM25 Encoder trained successfully.")

    def index_documents(self, chunks: List[Dict[str, Any]], batch_size: int = 50):
        """
        Upserts documents to Pinecone with dense and sparse vectors.
        Reduced batch_size to 50 because e5-large vectors are larger (1024 dim).
        """
        corpus = [chunk["content"] for chunk in chunks]

        if not hasattr(self.sparse_encoder, "idf_"):
            self.fit_sparse_encoder(corpus)

        print(f"Indexing {len(chunks)} documents into Pinecone...")

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            content_batch = [doc["content"] for doc in batch]
            ids = [doc["chunk_id"] for doc in batch]

            # Dense vectors with passage prefix
            dense_vectors = self._encode_documents(content_batch)

            # Sparse vectors (BM25)
            sparse_vectors = self.sparse_encoder.encode_documents(content_batch)

            vectors_to_upsert = []
            for j, doc in enumerate(batch):
                metadata = {
                    "text": doc["content"],
                    "source": doc["metadata"].get("source", "unknown"),
                    "page": str(doc["metadata"].get("page", "0")),
                    "language": doc.get("language", "en")  # store language in metadata
                }

                vectors_to_upsert.append({
                    "id": ids[j],
                    "values": dense_vectors[j],
                    "sparse_values": sparse_vectors[j],
                    "metadata": metadata
                })

            self.index.upsert(vectors=vectors_to_upsert)
            print(f"Upserted batch {i // batch_size + 1}. Total: {i + len(batch)}/{len(chunks)}")

        print(f"Indexing complete. Stats: {self.index.describe_index_stats()}")

    def hybrid_search(
        self,
        query: str,
        alpha: float = 0.5,
        k: int = 5,
        language_filter: str = None
    ) -> List[Document]:
        """
        Performs hybrid search using multilingual embeddings.
        Supports cross-lingual retrieval (German query → English docs and vice versa).

        Args:
            query: User query in any language (EN or DE)
            alpha: 0.0 = pure BM25, 1.0 = pure semantic, 0.5 = balanced
            k: Number of results to return
            language_filter: Optional — "en" or "de" to filter by document language
        """
        # Encode query with required prefix
        dense_query_vector = self._encode_query(query)
        sparse_query_vector = self.sparse_encoder.encode_queries(query)

        # Build filter if language specified
        filter_dict = None
        if language_filter:
            filter_dict = {"language": {"$eq": language_filter}}

        results = self.index.query(
            vector=dense_query_vector,
            sparse_vector=sparse_query_vector,
            top_k=k,
            include_metadata=True,
            alpha=alpha,
            filter=filter_dict
        )

        retrieved_docs = []
        for match in results.matches:
            doc = Document(
                page_content=match.metadata["text"],
                metadata={
                    "source": match.metadata["source"],
                    "page": match.metadata["page"],
                    "language": match.metadata.get("language", "en"),
                    "score": match.score
                }
            )
            retrieved_docs.append(doc)

        return retrieved_docs

    def run_ablation(
        self,
        query: str,
        alphas: List[float],
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """Runs retrieval across different alpha values for diagnostics."""
        ablation_results = []

        for alpha in alphas:
            print(f"Running ablation with alpha={alpha:.2f}")
            retrieved_docs = self.hybrid_search(query, alpha, k)

            result_summary = {
                "alpha": alpha,
                "k": k,
                "embedding_model": "multilingual-e5-large",
                "retrieved_documents": [
                    {
                        "text_snippet": doc.page_content[:150] + "...",
                        "source": doc.metadata["source"],
                        "page": doc.metadata["page"],
                        "language": doc.metadata.get("language", "en"),
                        "score": doc.metadata["score"]
                    }
                    for doc in retrieved_docs
                ]
            }
            ablation_results.append(result_summary)

        return ablation_results
