"""
Data Structures implementation for COVID Network Simulator.
Includes Adjacency List, HashSet (for tracking states), and Queue.
"""
from typing import List, Set, Dict, Optional
from collections import deque


class AdjacencyList:
    """Graph representation using Adjacency List."""
    
    def __init__(self):
        self.graph: Dict[int, List[int]] = {}
        self.nodes: Set[int] = set()
    
    def add_node(self, node: int) -> None:
        """Add a node to the graph."""
        if node not in self.graph:
            self.graph[node] = []
            self.nodes.add(node)
    
    def add_edge(self, u: int, v: int) -> None:
        """Add an undirected edge between u and v."""
        self.add_node(u)
        self.add_node(v)
        if v not in self.graph[u]:
            self.graph[u].append(v)
        if u not in self.graph[v]:
            self.graph[v].append(u)
    
    def get_neighbors(self, node: int) -> List[int]:
        """Get all neighbors of a node."""
        return self.graph.get(node, [])
    
    def get_degree(self, node: int) -> int:
        """Get the degree of a node."""
        return len(self.graph.get(node, []))
    
    def get_all_nodes(self) -> Set[int]:
        """Get all nodes in the graph."""
        return self.nodes.copy()
    
    def num_nodes(self) -> int:
        """Get the total number of nodes."""
        return len(self.nodes)
    
    def num_edges(self) -> int:
        """Get the total number of edges."""
        count = 0
        for neighbors in self.graph.values():
            count += len(neighbors)
        return count // 2
    
    def bfs(self, start: int) -> Set[int]:
        """Breadth-first search from a starting node."""
        visited = set()
        queue = deque([start])
        visited.add(start)
        
        while queue:
            node = queue.popleft()
            for neighbor in self.get_neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return visited
    
    def get_connected_components(self) -> List[Set[int]]:
        """Get all connected components in the graph."""
        visited = set()
        components = []
        
        for node in self.nodes:
            if node not in visited:
                component = self.bfs(node)
                components.append(component)
                visited.update(component)
        
        return components


class NodeStateSet:
    """HashSet for tracking node states efficiently."""
    
    def __init__(self):
        self.susceptible: Set[int] = set()
        self.infected: Set[int] = set()
        self.recovered: Set[int] = set()
        self.dead: Set[int] = set()
    
    def add_susceptible(self, node: int) -> None:
        """Mark a node as susceptible."""
        self.susceptible.add(node)
        self.infected.discard(node)
        self.recovered.discard(node)
        self.dead.discard(node)
    
    def add_infected(self, node: int) -> None:
        """Mark a node as infected."""
        self.infected.add(node)
        self.susceptible.discard(node)
        self.recovered.discard(node)
        self.dead.discard(node)
    
    def add_recovered(self, node: int) -> None:
        """Mark a node as recovered."""
        self.recovered.add(node)
        self.susceptible.discard(node)
        self.infected.discard(node)
        self.dead.discard(node)
    
    def add_dead(self, node: int) -> None:
        """Mark a node as dead."""
        self.dead.add(node)
        self.susceptible.discard(node)
        self.infected.discard(node)
        self.recovered.discard(node)
    
    def get_state(self, node: int) -> Optional[str]:
        """Get the state of a node."""
        if node in self.susceptible:
            return 'S'
        elif node in self.infected:
            return 'I'
        elif node in self.recovered:
            return 'R'
        elif node in self.dead:
            return 'D'
        return None
    
    def get_infected(self) -> Set[int]:
        """Get all infected nodes."""
        return self.infected.copy()
    
    def get_susceptible(self) -> Set[int]:
        """Get all susceptible nodes."""
        return self.susceptible.copy()
    
    def count_by_state(self) -> Dict[str, int]:
        """Count nodes by state."""
        return {
            'S': len(self.susceptible),
            'I': len(self.infected),
            'R': len(self.recovered),
            'D': len(self.dead)
        }


class InfectionQueue:
    """Queue for managing newly infected nodes."""
    
    def __init__(self):
        self.queue: deque = deque()
    
    def enqueue(self, node: int) -> None:
        """Add a node to the infection queue."""
        if node not in self.queue:
            self.queue.append(node)
    
    def dequeue(self) -> Optional[int]:
        """Remove and return a node from the queue."""
        if len(self.queue) > 0:
            return self.queue.popleft()
        return None
    
    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return len(self.queue) == 0
    
    def size(self) -> int:
        """Get the size of the queue."""
        return len(self.queue)
    
    def peek(self) -> Optional[int]:
        """View the next node without removing it."""
        if len(self.queue) > 0:
            return self.queue[0]
        return None
    
    def clear(self) -> None:
        """Clear the queue."""
        self.queue.clear()


class SimulationStatistics:
    """Track simulation statistics efficiently."""
    
    def __init__(self):
        self.history: List[Dict[str, int]] = []
        self.step: int = 0
    
    def record(self, s: int, i: int, r: int, d: int) -> None:
        """Record SIR statistics for the current step."""
        self.history.append({
            'step': self.step,
            'S': s,
            'I': i,
            'R': r,
            'D': d
        })
        self.step += 1
    
    def get_history(self) -> List[Dict[str, int]]:
        """Get the full history of statistics."""
        return self.history.copy()
    
    def get_peak_infected(self) -> int:
        """Get the peak number of infected nodes."""
        return max((h['I'] for h in self.history), default=0)
    
    def get_final_stats(self) -> Optional[Dict[str, int]]:
        """Get the final statistics."""
        return self.history[-1] if self.history else None
    
    def clear(self) -> None:
        """Clear all statistics."""
        self.history.clear()
        self.step = 0
