# src/agents/retriever_experiment_agent.py
import networkx as nx
import spacy
from typing import List, Dict, Any, Tuple
import os
import json

# Define the central entities we are tracking for the graph analysis
TARGET_ENTITIES = ["AI policy", "labour market reforms", "carbon transition measures", 
                   "employment protection", "health equity", "innovation"]

class RetrieverExperimentAgent:
    """
    Implements the GraphRAG architecture to analyze policy documents 
    based on entity linkage (co-occurrence).
    """
    def __init__(self):
        try:
            # Load the spaCy model (used for entity extraction)
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            # This is critical for entity extraction
            raise EnvironmentError("spaCy model 'en_core_web_sm' is required. Run: python -m spacy download en_core_web_sm")
        
        self.graph = nx.Graph()
        print("GraphRAG Agent initialized.")

    def _extract_entities_and_relationships(self, chunk: Dict[str, Any]) -> Tuple[List[str], List[Tuple[str, str, str]]]:
        """
        Extracts relevant entities and co-occurrence relationships from a text chunk.
        """
        doc = self.nlp(chunk['content'])
        
        extracted_entities = set()
        
        # 1. Extract based on NER labels (Organizations, Laws, Concepts)
        for ent in doc.ents:
            if ent.label_ in ["ORG", "GPE", "NORP", "LAW", "PRODUCT", "EVENT"]:
                extracted_entities.add(ent.text)
        
        # 2. Extract based on keyword match (for core policy themes)
        content_lower = chunk['content'].lower()
        for target in TARGET_ENTITIES:
            if target in content_lower:
                extracted_entities.add(target)
                
        # Simple Co-occurrence Relation
        relations = []
        entity_list = list(extracted_entities)
        
        for i in range(len(entity_list)):
            for j in range(i + 1, len(entity_list)):
                relations.append((entity_list[i], entity_list[j], chunk['metadata']['source']))
                
        return entity_list, relations

    def build_graph(self, processed_chunks: List[Dict[str, Any]]):
        """
        Builds the NetworkX graph from a list of processed chunks.
        Nodes are entities; edges represent co-occurrence in a document.
        """
        
        for i, chunk in enumerate(processed_chunks):
            entities, relations = self._extract_entities_and_relationships(chunk)
            
            # Add nodes and update node metadata (mentions count)
            for entity in entities:
                current_count = self.graph.nodes.get(entity, {}).get('count', 0)
                self.graph.add_node(entity, type='Policy Entity', count=current_count + 1)
            
            # Add edges and update edge weight (co-occurrence weight)
            for source, target, doc_source in relations:
                if self.graph.has_edge(source, target):
                    # If edge exists, increment weight and add document source
                    self.graph[source][target]['weight'] += 1
                    self.graph[source][target]['documents'].add(doc_source)
                else:
                    # Create new edge
                    self.graph.add_edge(source, target, weight=1, documents={doc_source})
                    
    def analyze_graph(self) -> Dict[str, Any]:
        """
        Identifies the most connected policy nodes using Centrality metrics.
        """
        if self.graph.number_of_nodes() == 0:
            return {"error": "Graph is empty."}
            
        # Degree Centrality: Simple count of connections (identifies 'policy themes')
        centrality = nx.degree_centrality(self.graph)

        N = min(100, self.graph.number_of_nodes())
        
        # Sort and get top 5 connected entities
        top_nodes = sorted(centrality.items(), key=lambda item: item[1], reverse=True)[:N]
        
        analysis = {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "most_connected_entities": [{
                "entity": node,
                "centrality_score": score,
                "document_mentions": self.graph.nodes[node].get('count', 0) 
            } for node, score in top_nodes]
        }
        return analysis