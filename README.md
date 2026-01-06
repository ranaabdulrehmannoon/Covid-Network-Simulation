# Covid-Network-Simulation
The Covid Network Simulation is a real-time simulation tool that models the spread and recovery of infectious diseases using graph-based networks.  The system visually tracks live infections (attacks) and recoveries, allowing analysis of disease propagation, hotspot identification, and recovery dynamics in a simulated population.

# COVID Network Simulator — 3D Web + API

A professional web-based epidemic simulator with 3D network visualization, real-time SIR dynamics tracking, and interactive disease spread simulation. This project combines a high-performance Python backend with a modern React 3D frontend to visualize how viruses spread through complex networks.

## 🚀 Tech Stack

### Frontend
- **React 18**: UI component architecture
- **Vite**: Next-generation frontend tooling
- **Three.js**: High-performance 3D graphics rendering
- **Chart.js**: Real-time statistical data visualization
- **CSS3**: Custom styling with responsive design

### Backend
- **Python 3.10+**: Core logic and API
- **FastAPI**: High-performance web framework for building APIs
- **NetworkX**: Complex network creation, manipulation, and study
- **Pandas & NumPy**: Data analysis and numerical computing
- **Scikit-learn**: Text similarity analysis (TF-IDF) for network generation

## 📚 Libraries Used

| Library | Purpose |
|---------|---------|
| `fastapi` | REST API endpoints for graph generation and simulation |
| `uvicorn` | ASGI server implementation |
| `networkx` | Graph data structures and algorithms |
| `pandas` | CSV data processing and manipulation |
| `numpy` | Efficient numerical operations and random number generation |
| `three` | 3D rendering engine for the network visualization |
| `react-chartjs-2` | React wrapper for Chart.js |

## 🧠 Data Structures & Algorithms

The project utilizes efficient data structures to handle network operations and simulation dynamics:

### 1. Graph Representation
- **Adjacency List**: The core network is represented using NetworkX's internal adjacency structure (dict-of-dicts). This allows for **O(1)** average time complexity for checking edge existence and efficient neighbor iteration.

### 2. Simulation State Management
- **Hash Sets (`set`)**: Used during simulation steps (`to_infect`, `to_recover`, `to_die`) to track state transitions. This ensures unique handling of nodes and provides **O(1)** lookups and insertions.
- **Hash Maps (`dict`)**: 
  - `node_states`: Maps Node IDs to their current state ('S', 'I', 'R', 'D').
  - `pos`: Stores 3D coordinates (x, y, z) for each node.
- **Arrays/Lists**: Used to store the simulation history (time-series data) for the charts.

### 3. Network Generation Algorithms
- **Barabási–Albert Model**: Generates scale-free networks using preferential attachment (hubs form naturally).
- **Erdős–Rényi Model**: Generates random graphs where each edge has a fixed probability.
- **Watts–Strogatz Model**: Generates small-world networks with high clustering coefficients.
- **Stochastic Block Model**: Generates networks with community structure.

## 🎲 Probabilities & Simulation Logic

The simulation implements an extended **SIR (Susceptible-Infected-Recovered)** model with a **Death (D)** state. The simulation proceeds in discrete time steps.

### Core Logic Flow
For every time step $t$:
1. Iterate through all nodes in the graph.
2. If a node is **Infected (I)**, three mutually exclusive events are evaluated based on probabilities:

#### 1. Death Probability ($P_d$)
The probability that an infected individual dies at the current step.
- **Implementation**: `if random() < death_prob: node -> Dead`
- **Effect**: The node is removed from the network dynamics (cannot infect others).

#### 2. Infection Spread ($P_i$)
The probability that an infected node transmits the virus to a connected **Susceptible (S)** neighbor.
- **Implementation**: 
  ```python
  for neighbor in neighbors:
      if neighbor is Susceptible:
          if random() < infection_prob: 
              neighbor -> Infected (next step)
  ```
- **Effect**: The virus propagates through the network edges.

#### 3. Recovery Probability ($P_r$)
The probability that an infected node recovers and becomes immune.
- **Implementation**: `if random() < recovery_prob: node -> Recovered`
- **Note**: In this system, $P_r$ is randomized per node (uniform distribution between 0.3 and 0.9) to simulate varying immune system strengths.

### State Updates
All state changes are applied **synchronously** at the end of each step. This prevents a node from being infected and then infecting others in the exact same time step (simulating simultaneous interaction).

## 📂 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entry point & endpoints
│   │   └── simulator.py     # Core simulation engine & graph logic
│   └── requirements.txt     # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component & UI logic
│   │   ├── api.js           # API communication layer
│   │   └── index.css        # Global styles
│   └── package.json         # Node dependencies
```

## 🛠️ Setup & Running

### Backend
```bash
cd backend
python -m venv .venv
# Windows:
.\.venv\Scripts\Activate.ps1
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
The frontend will be available at `http://localhost:5173` (default Vite port).
=======
# Covid-Network-Simulation
>>>>>>> 5fb484ac7da5dc35aa4f6cc43f1669e9a0af8c18
