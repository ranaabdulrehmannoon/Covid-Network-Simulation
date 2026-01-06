# COVID Network Simulator: Technical Implementation Report

## 1. Executive Summary
The COVID Network Simulator is a full-stack web application designed to visualize and simulate the spread of an epidemic through complex social networks. By combining a high-performance Python backend for graph theory computations with a React-based 3D visualization frontend, the system provides an interactive platform for understanding SIR (Susceptible-Infected-Recovered) dynamics. The application allows users to generate synthetic networks (Small-world, Scale-free, Random) or upload custom datasets, and then observe in real-time how a virus propagates through the nodes based on configurable probabilistic parameters.

## 2. System Architecture

### 2.1 High-Level Overview
The system follows a decoupled client-server architecture:
- **Backend (API Layer)**: Built with FastAPI and Python, responsible for heavy computational tasks including graph generation, network analysis, and running the step-by-step simulation logic.
- **Frontend (Presentation Layer)**: Built with React 18 and Three.js, responsible for rendering the 3D interactive graph, managing user state, and displaying real-time statistical charts.

### 2.2 Technology Stack
| Component | Technology | Justification |
|-----------|------------|---------------|
| **Backend Framework** | FastAPI (Python) | High performance, native async support, and easy integration with data science libraries. |
| **Graph Processing** | NetworkX | Industry standard for complex network analysis and algorithmic generation. |
| **Data Handling** | Pandas & NumPy | Efficient manipulation of large datasets and vectorized numerical operations. |
| **Frontend Framework** | React 18 | Component-based architecture for managing complex UI state. |
| **3D Visualization** | Three.js | WebGL-based rendering for performant 3D graphics in the browser. |
| **Charting** | Chart.js | Responsive, canvas-based charting for real-time data visualization. |

## 3. Data Structures and Algorithms

### 3.1 Graph Representation
The core of the application relies on efficient graph data structures to handle network operations.
- **Adjacency List**: The network is stored using an adjacency list (implemented via NetworkX's dict-of-dicts).
  - **Space Complexity**: $O(V + E)$, where $V$ is vertices and $E$ is edges.
  - **Time Complexity**: $O(1)$ for checking edge existence; $O(deg(v))$ for iterating neighbors.
  - **Reasoning**: Social networks are typically sparse (density $\ll$ 1). An adjacency matrix would require $O(V^2)$ space, which is inefficient.

### 3.2 Simulation State Management
To ensure the simulation runs efficiently ($O(V+E)$ per step), specific data structures were chosen:
- **Hash Sets (`set`)**: Used for tracking `to_infect`, `to_recover`, and `to_die` nodes during a simulation step.
  - **Benefit**: Provides $O(1)$ average time complexity for insertions and lookups, preventing duplicate processing of nodes.
- **Hash Maps (`dict`)**:
  - `node_states`: Maps Node IDs to states ('S', 'I', 'R', 'D').
  - `pos`: Stores 3D coordinates $(x, y, z)$ for visualization.

### 3.3 Network Generation Algorithms
The system implements four distinct graph generation algorithms to model different types of social structures:

1.  **Watts–Strogatz (Small-World)**:
    -   **Mechanism**: Starts with a ring lattice and rewires edges with probability $p$.
    -   **Use Case**: Models social networks with high clustering (friends of friends are friends) and short average path lengths.

2.  **Barabási–Albert (Scale-Free)**:
    -   **Mechanism**: Nodes are added one by one, connecting to existing nodes with probability proportional to their current degree (Preferential Attachment).
    -   **Use Case**: Models networks with "hubs" or super-spreaders (e.g., influencers, public transport hubs).

3.  **Erdős–Rényi (Random)**:
    -   **Mechanism**: Every possible edge is created with a fixed probability $p$.
    -   **Use Case**: Serves as a baseline for comparison, though less realistic for human social networks.

4.  **Stochastic Block Model (Community Structure)**:
    -   **Mechanism**: Nodes are assigned to communities; edges within communities are more likely than edges between them.
    -   **Use Case**: Models schools, workplaces, or cities where internal interaction is high.

## 4. Simulation Logic (SIR+D Model)

The simulation implements a discrete-time stochastic process. At each time step $t$, the system updates the state of the network based on the following probabilistic rules:

### 4.1 State Transitions
1.  **Infection ($S \to I$)**:
    -   An infected node $u$ attempts to infect each susceptible neighbor $v$.
    -   Success occurs if $random() < P_{infection}$.
2.  **Recovery ($I \to R$)**:
    -   An infected node recovers with probability $P_{recovery}$.
    -   $P_{recovery}$ is randomized per node (Uniform distribution $[0.3, 0.9]$) to simulate biological variance in immune systems.
3.  **Death ($I \to D$)**:
    -   An infected node dies with probability $P_{death}$.
    -   Dead nodes are removed from the active network (degree effectively becomes 0).

### 4.2 Synchronous Update
To prevent cascading updates within a single time step (which would simulate infinite speed of transmission), the simulation uses a **synchronous update** scheme:
1.  Calculate all potential transitions based on the state at time $t$.
2.  Store pending changes in temporary sets.
3.  Apply all changes simultaneously to produce the state at time $t+1$.

## 5. Frontend Implementation Details

### 5.1 3D Visualization (Three.js)
-   **Rendering**: Uses a `WebGLRenderer` to display nodes (Spheres) and edges (Lines).
-   **Performance Optimization**:
    -   **Geometry Instancing**: Reuses geometry objects to reduce memory footprint.
    -   **Ref-based Animation Loop**: The animation loop uses React `useRef` hooks to bypass the React render cycle for high-frequency updates (60 FPS), updating object positions and colors directly in the DOM.
    -   **React.memo**: The `Network3D` component is memoized to prevent re-rendering the entire canvas when parent state changes (e.g., updating the step counter).

### 5.2 Real-time Charting
-   Uses `react-chartjs-2` to render a line chart tracking the population of S, I, R, and D groups over time.
-   Data is fed from the simulation history array, providing immediate visual feedback on the "flattening of the curve."

## 6. Conclusion
The COVID Network Simulator successfully demonstrates the application of graph theory and probabilistic modeling to epidemiology. By leveraging efficient data structures (Adjacency Lists, Hash Sets) and modern web technologies, the system provides a performant and educational tool for understanding how network topology influences disease spread. The modular architecture allows for easy extension, such as adding new network types or more complex disease states (e.g., Exposed, Asymptomatic).
