# run_task_3.py
import os
import json
from src.agents.retriever_agent import RetrieverAgent
from src.utils import save_json
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
INPUT_FILE = 'D:/NLP_Final_Project/Examination-master/results/classical_output.json'
RETRIEVAL_DIAGNOSTICS_OUTPUT = 'D:/NLP_Final_Project/Examination-master/results/retrieval_ablation.json'
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "policy-rag-index")

# UPDATED: 1024 for multilingual-e5-large
EMBEDDING_DIMENSION = 1024

# Test queries — English AND German to showcase bilingual retrieval
TEST_QUERY_EN = "Compare fiscal strategies for financing climate goals across OECD and IMF documents."
TEST_QUERY_DE = "Wie bewertet die Bundesbank die Inflationsentwicklung in Deutschland?"

def run_task_3():
    """Executes the Hybrid Retrieval and Ablation task."""
    print("--- Starting Task 3: Hybrid Retrieval (BM25 + Pinecone) ---")
    print(f"Embedding model: intfloat/multilingual-e5-large (dim={EMBEDDING_DIMENSION})")

    # 1. Environment checks
    if not all([os.getenv("PINECONE_API_KEY"), os.getenv("PINECONE_ENVIRONMENT")]):
        print("ERROR: Missing PINECONE_API_KEY or PINECONE_ENVIRONMENT in .env")
        return

    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: {INPUT_FILE} not found. Run run_task_1.py first.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        processed_chunks = json.load(f)

    print(f"Loaded {len(processed_chunks)} chunks for indexing.")

    # 2. Initialize RetrieverAgent with new dimension
    retriever_agent = RetrieverAgent(
        index_name=PINECONE_INDEX_NAME,
        dimension=EMBEDDING_DIMENSION,
        sbert_model="intfloat/multilingual-e5-large"
    )

    # 3. Index all documents
    retriever_agent.index_documents(processed_chunks)

    # 4. Run ablation — both English and German queries
    alphas = [0.2, 0.4, 0.6, 0.8]

    print("\n--- Running Retrieval Ablation (English query) ---")
    ablation_en = retriever_agent.run_ablation(TEST_QUERY_EN, alphas, k=5)

    print("\n--- Running Retrieval Ablation (German query) ---")
    ablation_de = retriever_agent.run_ablation(TEST_QUERY_DE, alphas, k=5)

    # 5. Save diagnostics
    retrieval_diagnostics = {
        "embedding_model": "intfloat/multilingual-e5-large",
        "dimension": EMBEDDING_DIMENSION,
        "english_query": {
            "query": TEST_QUERY_EN,
            "ablation_results": ablation_en
        },
        "german_query": {
            "query": TEST_QUERY_DE,
            "ablation_results": ablation_de
        }
    }

    save_json(retrieval_diagnostics, RETRIEVAL_DIAGNOSTICS_OUTPUT)
    print("\n--- Task 3 Completed Successfully ---")

if __name__ == "__main__":
    run_task_3()