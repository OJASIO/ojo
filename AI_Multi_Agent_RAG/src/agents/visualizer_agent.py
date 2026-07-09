# src/agents/visualizer_agent.py (CONSOLIDATED & FIXED for missing methods)
import matplotlib.pyplot as plt
import networkx as nx
import os
import numpy as np # Needed for array operations
from sklearn.manifold import TSNE # Needed for t-SNE
from sklearn.decomposition import PCA # Needed for PCA
from typing import Dict, Any, List

# NOTE: Ensure matplotlib.use('Agg') is placed in run_task_2.py 
# and run_task_7.py *before* importing this file.

class VisualizerAgent:
    """
    Plots historical metrics and the conceptual agent graph (Task 7)
    and embedding diagnostics (Task 2).
    """
    def __init__(self, output_dir: str = 'results/plots'):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def _reduce_and_plot(self, embeddings: np.ndarray, method: str, title: str, filename: str, labels: np.ndarray):
        """Reduces dimensions and plots the result (Helper for Task 2 plots)."""
        
        print(f"Reducing {method} embeddings with {'t-SNE' if method=='t-sne' else 'PCA'}...")
        
        # 1. Dimensionality Reduction
        if method == 't-sne':
            if embeddings.shape[1] > 50:
                embeddings = PCA(n_components=50, random_state=42).fit_transform(embeddings)
            
            reducer = TSNE(n_components=2, random_state=42, n_jobs=-1, perplexity=30, init='pca', learning_rate='auto')
            reduced_data = reducer.fit_transform(embeddings)
        else: # PCA
            reducer = PCA(n_components=2, random_state=42)
            reduced_data = reducer.fit_transform(embeddings)

        # 2. Plotting
        plt.figure(figsize=(10, 8))
        
        # Plot, coloring points by their dominant topic label
        scatter = plt.scatter(reduced_data[:, 0], reduced_data[:, 1], 
                              c=labels, cmap='Spectral', alpha=0.7)
            
        # Add legend
        legend1 = plt.legend(*scatter.legend_elements(), 
                            title="Topic Index", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.gca().add_artist(legend1)
        
        plt.title(f'{title} (2D Projection via {method.upper()})')
        plt.xlabel('Component 1')
        plt.ylabel('Component 2')
        plt.grid(True, linestyle='--', alpha=0.6)
        
        # Save the plot
        full_path = os.path.join(self.output_dir, filename)
        plt.savefig(full_path, bbox_inches='tight')
        plt.close()
        print(f"Saved plot to {full_path}")
        return full_path

    # --- MISSING METHOD: visualize_embeddings (Task 2) ---
    def visualize_embeddings(self, embedding_dict: Dict[str, np.ndarray], doc_topic_matrix: np.ndarray,output_dir: str) -> List[str]:
        """Runs the reduction and plotting for both SBERT and TFIDF representations."""
        
        # Determine the dominant topic for each document/chunk (our "labels")
        dominant_topics = np.argmax(doc_topic_matrix, axis=1)
        
        saved_plots = []
        
        # SBERT Visualization
        path_sbert = self._reduce_and_plot(
            embeddings=embedding_dict['sbert'], 
            method='t-sne', 
            title='SBERT (Transformer) Embeddings',
            filename='sbert_t_sne.png',
            labels=dominant_topics
        )
        saved_plots.append(path_sbert)

        # TF-IDF Visualization
        path_tfidf = self._reduce_and_plot(
            embeddings=embedding_dict['tfidf'], 
            method='pca', 
            title='TF-IDF (Classical) Embeddings',
            filename='tfidf_pca.png',
            labels=dominant_topics
        )
        saved_plots.append(path_tfidf)

        return saved_plots

    # --- EXISTING METHOD: plot_confidence_trajectory (Task 7) ---
    def plot_confidence_trajectory(self, memory_history: List[Dict[str, Any]]) -> str:
        # ... (Your existing code here, which is correct for Task 7) ...
        runs = list(range(1, len(memory_history) + 1))
        entailment_rates = [run['metrics']['entailment_rate'] for run in memory_history]
        alphas = [run['retrieval_params']['alpha'] for run in memory_history]
        
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Plot 1: Entailment Rate (Factual Precision)
        color = 'tab:blue'
        ax1.set_xlabel('Run Number')
        ax1.set_ylabel('Factual Entailment Rate (Verification)', color=color)
        ax1.plot(runs, entailment_rates, color=color, marker='o')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.set_ylim(0, 1.05)
        ax1.grid(True, linestyle='--', alpha=0.6)

        # Plot 2: Adaptive Alpha Parameter
        ax2 = ax1.twinx()  
        color = 'tab:red'
        ax2.set_ylabel(r'Hybrid RAG Alpha ($\alpha$)', color=color)  # Use raw string for LaTeX
        ax2.plot(runs, alphas, color=color, marker='x', linestyle='--')
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.set_ylim(0, 1.05)

        fig.tight_layout()
        plt.title(r'Pipeline Adaptivity: Factual Precision vs. $\alpha$ Parameter')
        
        plot_path = os.path.join(self.output_dir, 'confidence_trajectory.png')
        plt.savefig(plot_path)
        plt.close()
        return plot_path

    # --- EXISTING METHOD: plot_agent_graph (Task 7) ---
    def plot_agent_graph(self) -> str:
        """Plots a simplified conceptual diagram of the multi-agent workflow."""
        # ... (Your existing code here, which is correct for Task 7) ...
        G = nx.DiGraph()
        
        # Define Nodes (Agents/Components)
        nodes = {
            'A': 'Planner', 'B': 'Retriever', 'C': 'Summarizer', 
            'D': 'Debate', 'E': 'Verifier', 'F': 'Guardrails', 
            'M': 'Memory/Tune', 'V': 'Visualization'
        }
        
        # Define Edges (Flow/Communication)
        edges = [
            ('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'E'), ('E', 'F'), ('F', 'C'),
            ('E', 'M'), ('F', 'M'), # Log metrics to Memory
            ('M', 'B'), # Tune Retrieval (Alpha/k)
            ('M', 'V') # Data to Visualization
        ]
        
        G.add_nodes_from(nodes.keys())
        G.add_edges_from(edges)
        
        pos = nx.spring_layout(G, seed=42)
        
        plt.figure(figsize=(12, 8))
        nx.draw(
            G, pos, 
            with_labels=True, 
            labels=nodes, 
            node_size=3000, 
            node_color="skyblue", 
            font_size=10, 
            font_weight="bold", 
            arrowsize=20
        )
        plt.title("Multi-Agent RAG Pipeline Architecture (LangGraph Concept)")
        
        plot_path = os.path.join(self.output_dir, 'agent_graph.png')
        plt.savefig(plot_path)
        plt.close()
        return plot_path