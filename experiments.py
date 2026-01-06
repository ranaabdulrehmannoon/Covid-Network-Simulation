"""
Experiments module for analyzing disease spread across different network types
and infection probabilities.
"""
import networkx as nx
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from data_structures import AdjacencyList, NodeStateSet, SimulationStatistics
import random


class DiseaseSimulator:
    """Simulate SIR disease spread on a network."""
    
    def __init__(self, graph: nx.Graph, infection_prob: float = 0.5, death_prob: float = 0.12):
        self.graph = graph
        self.infection_prob = max(0.01, min(1.0, infection_prob))
        self.death_prob = max(0, min(1, death_prob))
        self.states = NodeStateSet()
        self.stats = SimulationStatistics()
        self._initialize_nodes()
    
    def _initialize_nodes(self) -> None:
        """Initialize all nodes as susceptible."""
        for node in self.graph.nodes():
            self.states.add_susceptible(node)
    
    def set_initial_infected(self, count: int = 3) -> None:
        """Randomly infect initial nodes."""
        nodes = list(self.graph.nodes())
        count = min(count, len(nodes))
        infected = random.sample(nodes, count)
        for node in infected:
            self.states.add_infected(node)
    
    def simulate_step(self) -> bool:
        """Execute one step of the simulation. Returns True if simulation continues."""
        to_infect = set()
        to_recover = set()
        to_die = set()
        
        for node in self.states.get_infected():
            if random.random() < self.death_prob:
                to_die.add(node)
                continue
            
            for neighbor in self.graph.neighbors(node):
                if self.states.get_state(neighbor) == 'S':
                    if random.random() < self.infection_prob:
                        to_infect.add(neighbor)
            
            if random.random() < 0.5:
                to_recover.add(node)
        
        for node in to_infect:
            self.states.add_infected(node)
        for node in to_recover:
            self.states.add_recovered(node)
        for node in to_die:
            self.states.add_dead(node)
        
        counts = self.states.count_by_state()
        self.stats.record(counts['S'], counts['I'], counts['R'], counts['D'])
        
        return counts['I'] > 0
    
    def run(self, max_steps: int = 1000) -> List[Dict[str, int]]:
        """Run the full simulation."""
        self.stats.clear()
        self._initialize_nodes()
        self.set_initial_infected(3)
        
        counts = self.states.count_by_state()
        self.stats.record(counts['S'], counts['I'], counts['R'], counts['D'])
        
        step = 0
        while step < max_steps and self.simulate_step():
            step += 1
        
        return self.stats.get_history()


class NetworkAnalyzer:
    """Analyze network properties."""
    
    @staticmethod
    def analyze(graph: nx.Graph, name: str) -> Dict:
        """Analyze key properties of a network."""
        if graph.number_of_nodes() == 0:
            return {
                'name': name,
                'nodes': 0,
                'edges': 0,
                'avg_degree': 0,
                'clustering': 0,
                'avg_shortest_path': 0,
                'diameter': 0
            }
        
        components = list(nx.connected_components(graph))
        largest = graph.subgraph(components[0]).copy() if components else graph
        
        return {
            'name': name,
            'nodes': graph.number_of_nodes(),
            'edges': graph.number_of_edges(),
            'avg_degree': 2 * graph.number_of_edges() / graph.number_of_nodes() if graph.number_of_nodes() > 0 else 0,
            'clustering': nx.average_clustering(graph),
            'avg_shortest_path': nx.average_shortest_path_length(largest) if largest.number_of_nodes() > 1 else 0,
            'diameter': nx.diameter(largest) if nx.is_connected(largest) else -1,
            'num_components': len(components)
        }


def run_experiment_varying_infection_prob(graph: nx.Graph, name: str, iterations: int = 5) -> pd.DataFrame:
    """Run experiment varying infection probability."""
    results = []
    
    for prob in np.linspace(0.1, 0.9, 9):
        peak_infected = []
        final_recovered = []
        
        for _ in range(iterations):
            sim = DiseaseSimulator(graph, infection_prob=prob, death_prob=0.12)
            history = sim.run()
            
            peak_i = max((h['I'] for h in history), default=0)
            final_r = history[-1]['R'] if history else 0
            
            peak_infected.append(peak_i)
            final_recovered.append(final_r)
        
        results.append({
            'network': name,
            'infection_prob': prob,
            'peak_infected_avg': np.mean(peak_infected),
            'peak_infected_std': np.std(peak_infected),
            'final_recovered_avg': np.mean(final_recovered),
            'final_recovered_std': np.std(final_recovered)
        })
    
    return pd.DataFrame(results)


def run_experiment_network_comparison(networks: Dict[str, nx.Graph], iterations: int = 5) -> pd.DataFrame:
    """Compare disease spread across different network types."""
    results = []
    
    for name, graph in networks.items():
        analysis = NetworkAnalyzer.analyze(graph, name)
        
        peak_infected = []
        final_recovered = []
        total_steps = []
        
        for _ in range(iterations):
            sim = DiseaseSimulator(graph, infection_prob=0.5, death_prob=0.12)
            history = sim.run()
            
            peak_i = max((h['I'] for h in history), default=0)
            final_r = history[-1]['R'] if history else 0
            
            peak_infected.append(peak_i)
            final_recovered.append(final_r)
            total_steps.append(len(history))
        
        result = {
            'network': name,
            'nodes': analysis['nodes'],
            'edges': analysis['edges'],
            'avg_degree': analysis['avg_degree'],
            'clustering': analysis['clustering'],
            'avg_shortest_path': analysis['avg_shortest_path'],
            'peak_infected_avg': np.mean(peak_infected),
            'peak_infected_std': np.std(peak_infected),
            'final_recovered_avg': np.mean(final_recovered),
            'final_recovered_std': np.std(final_recovered),
            'avg_steps': np.mean(total_steps)
        }
        results.append(result)
    
    return pd.DataFrame(results)


if __name__ == "__main__":
    print("Running experiments...\n")
    
    print("1. Generating networks...")
    ws_small = nx.watts_strogatz_graph(100, 8, 0.1, seed=42)
    ws_medium = nx.watts_strogatz_graph(200, 10, 0.1, seed=42)
    ba = nx.barabasi_albert_graph(100, 4, seed=42)
    er = nx.erdos_renyi_graph(100, 0.08, seed=42)
    
    print("2. Comparing networks...")
    networks = {
        'Watts-Strogatz (100 nodes)': ws_small,
        'Watts-Strogatz (200 nodes)': ws_medium,
        'Barabasi-Albert': ba,
        'Erdos-Renyi': er
    }
    
    comparison = run_experiment_network_comparison(networks, iterations=3)
    print("\nNetwork Comparison Results:")
    print(comparison.to_string())
    comparison.to_csv('experiment_network_comparison.csv', index=False)
    
    print("\n3. Varying infection probability...")
    prob_results = run_experiment_varying_infection_prob(ws_small, 'Watts-Strogatz (100)', iterations=3)
    print("\nInfection Probability Variation Results:")
    print(prob_results.to_string())
    prob_results.to_csv('experiment_infection_probability.csv', index=False)
    
    print("\nExperiments completed! Results saved to CSV files.")
