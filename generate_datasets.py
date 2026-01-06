#!/usr/bin/env python3
"""
Generate sample Watts-Strogatz networks for testing and analysis.
"""
import networkx as nx
import pandas as pd
import os

def generate_watts_strogatz_dataset(n_nodes, k, p, filename):
    """Generate a Watts-Strogatz network and save as edge list CSV."""
    G = nx.watts_strogatz_graph(n_nodes, k, p, seed=42)
    
    edges = []
    for u, v in G.edges():
        edges.append({"FromNodeId": u, "ToNodeId": v})
    
    df = pd.DataFrame(edges)
    df.to_csv(filename, index=False)
    
    print(f"Generated {filename}")
    print(f"  Nodes: {G.number_of_nodes()}")
    print(f"  Edges: {G.number_of_edges()}")
    print(f"  Avg degree: {2 * G.number_of_edges() / G.number_of_nodes():.2f}")
    print(f"  Clustering coefficient: {nx.average_clustering(G):.4f}")
    print(f"  Average shortest path: {nx.average_shortest_path_length(G):.4f}")
    print()

if __name__ == "__main__":
    print("Generating Watts-Strogatz networks...\n")
    
    generate_watts_strogatz_dataset(100, 8, 0.1, "watts_strogatz_100.csv")
    generate_watts_strogatz_dataset(500, 10, 0.1, "watts_strogatz_500.csv")
    generate_watts_strogatz_dataset(1000, 12, 0.1, "watts_strogatz_1000.csv")
    
    print("All datasets generated successfully!")
