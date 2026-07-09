# run_task_2.py
import os
import numpy as np
from src.agents.topic_model_agent import TopicModelAgent
from src.agents.embedding_agent import EmbeddingAgent
from src.agents.visualizer_agent import VisualizerAgent
from src.utils import save_json # Assuming utils.py has the save_json function
import json
from typing import List, Dict, Any
import matplotlib
matplotlib.use('Agg')

# --- Configuration ---
INPUT_FILE = 'D:/NLP_Final_Project/Examination-master/results/classical_output.json'
DIAGNOSTICS_OUTPUT = 'D:/NLP_Final_Project/Examination-master/results/topic_model_diagnostics.json'
EMBEDDING_MAP_DIR = 'D:/NLP_Final_Project/Examination-master/results/plots' # Plots are saved here

def run_task_2():
    """Executes Topic Modeling and Embedding Diagnostics."""
    print("--- Starting Task 2: Topic Modeling & Representation Diagnostics ---")

    # 1. Load Pre-Processed Data from Task 1
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: Task 1 output file not found at {INPUT_FILE}.")
        print("ACTION REQUIRED: Please run 'python run_task_1.py' first.")
        return
        
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            processed_chunks = json.load(f)
    except Exception as e:
        print(f"Error loading Task 1 JSON: {e}")
        return
        
    print(f"Loaded {len(processed_chunks)} chunks from Task 1.")

    # 2. Topic Modeling (NMF)
    topic_agent = TopicModelAgent(n_topics=10)
    topic_descriptions, doc_topic_matrix = topic_agent.train_topic_model(processed_chunks)
    print("\nTopic Descriptions:")
    for desc in topic_descriptions:
        print(f" - {desc}")

    # 3. Embedding Generation
    embedding_agent = EmbeddingAgent()
    embedding_dict = embedding_agent.build_embeddings(processed_chunks)
    
    # 4. Visualization (t-SNE / PCA)
    visualizer_agent = VisualizerAgent()
    
    # Use the embeddings and the topic matrix to generate colored plots
    plot_paths = visualizer_agent.visualize_embeddings(embedding_dict, doc_topic_matrix, EMBEDDING_MAP_DIR)

    # 5. Save Topic Model Diagnostics
    diagnostics = {
        "topics": topic_descriptions,
        "n_chunks": len(processed_chunks),
        "topic_model_type": "NMF",
        "embedding_models": ["SBERT/all-MiniLM-L6-v2", "TF-IDF"],
        "embedding_plots_saved": plot_paths,
        "document_topic_matrix_shape": doc_topic_matrix.shape,
    }
    save_json(diagnostics, DIAGNOSTICS_OUTPUT)
    
    print("\n--- Task 2 Completed Successfully ---")

if __name__ == "__main__":
    run_task_2()