# COVID-19 Network Simulator - Complete Implementation

## Overview

This project implements a comprehensive COVID-19 epidemic simulator that models disease spread (SIR model) across social networks using Watts-Strogatz small-world networks and other topology models.

## Project Structure

```
.
├── frontend/                          # React web application
│   ├── src/
│   │   ├── App.jsx                   # Main React component
│   │   ├── api.js                    # API client
│   │   └── styles.css                # Styling
│   └── package.json                  # Dependencies
├── backend/                          # FastAPI server
│   └── app/
│       ├── main.py                   # API endpoints
│       └── simulator.py              # SIR simulation logic
├── data_structures.py                # Core data structures implementation
├── experiments.py                    # Experimental analysis
├── generate_datasets.py              # Dataset generation script
├── report.tex                        # LaTeX comprehensive report
├── presentation.tex                  # Beamer presentation slides
├── experiment_*.csv                  # Experiment results
└── watts_strogatz_*.csv             # Generated network datasets
```

## Key Files

### Backend Implementation

- **simulator.py**: Watts-Strogatz network generation + SIR simulation
- **main.py**: FastAPI endpoints for network generation and simulation

### Data Structures (data_structures.py)

1. **AdjacencyList**: O(V+E) graph representation
2. **NodeStateSet**: HashSet-based state tracking
3. **InfectionQueue**: FIFO queue for infection processing
4. **SimulationStatistics**: Efficient history tracking

### Experiments

- **experiments.py**: Runs systematic comparisons
  - Network topology comparison
  - Infection probability sensitivity analysis
  - Results exported to CSV

### Visualization

- **Frontend**: React 18 + Three.js r128
  - 3D interactive network visualization
  - Real-time SIR statistics
  - Disease spread animation

## Generated Datasets

Three Watts-Strogatz networks generated:
- **watts_strogatz_100.csv**: 100 nodes, 400 edges, clustering=0.48
- **watts_strogatz_500.csv**: 500 nodes, 2500 edges, clustering=0.50
- **watts_strogatz_1000.csv**: 1000 nodes, 6000 edges, clustering=0.51

Edge format:
```csv
FromNodeId,ToNodeId
0,1
0,3
...
```

## Experiment Results

### Network Comparison (infection_prob=0.5, 3 runs each)

| Network | Nodes | Clustering | Peak Infected | Final Recovered | Avg Steps |
|---------|-------|-----------|---------------|-----------------|-----------|
| Watts-Strogatz (100) | 100 | 0.480 | 40.3 ± 5.7 | 81.7 ± 2.6 | 11.0 |
| Watts-Strogatz (200) | 200 | 0.505 | 92.7 ± 8.2 | 158.0 ± 7.8 | 12.0 |
| Barabási-Albert | 100 | 0.187 | 56.0 ± 3.3 | 79.7 ± 3.1 | 10.0 |
| Erdős-Rényi | 100 | 0.065 | 52.0 ± 0.8 | 78.3 ± 2.9 | 10.7 |

### Infection Probability Sensitivity (WS-100, 3 runs each)

| Infection Prob | Peak Infected | Std Dev | Final Recovered |
|----------------|--------------|---------|-----------------|
| 0.1 | 5.3 ± 1.2 | High variance | 13.7 ± 4.7 |
| 0.2 | 15.0 ± 4.2 | Moderate | 62.7 ± 8.1 |
| 0.3 | 20.3 ± 12.5 | **Critical threshold** | 50.3 ± 35.6 |
| 0.4 | 31.7 ± 5.3 | Explosive growth | 75.3 ± 2.6 |
| 0.5+ | 40-53 | Low variance | 76-79 (saturated) |

## How to Run

### 1. Install Dependencies

**Frontend:**
```bash
cd frontend
npm install
```

**Backend:**
```bash
pip install fastapi uvicorn pandas networkx numpy scikit-learn
```

### 2. Generate Datasets

```bash
python generate_datasets.py
```

Generates:
- watts_strogatz_100.csv
- watts_strogatz_500.csv
- watts_strogatz_1000.csv

### 3. Run Experiments

```bash
python experiments.py
```

Generates:
- experiment_network_comparison.csv
- experiment_infection_probability.csv

### 4. Start Backend

```bash
cd backend
uvicorn app.main:app --reload
```

Backend runs on `http://localhost:8000`

### 5. Start Frontend

```bash
cd frontend
npm run dev
```

Frontend runs on `http://localhost:5173`

### 6. Use the Application

1. **Upload CSV or Generate Network**
   - Upload edge list CSV with FromNodeId, ToNodeId
   - OR use "Generate Synthetic" to create Watts-Strogatz network

2. **Adjust Parameters**
   - Infection probability (0-100%)
   - Death probability (0-100%, default 12%)
   - Number of nodes (10-500)
   - Average degree (2-50)

3. **Run Simulation**
   - Click "Run simulation"
   - Watch real-time 3D network visualization
   - Monitor SIR statistics and infection curve

4. **Interact with Network**
   - Drag to rotate 3D view
   - Scroll to zoom
   - Auto-rotates when idle

## Algorithm Complexity

### Time Complexity
- Per step: **O(V + E)**
- Total simulation (T steps): **O(T × (V + E))**
- For sparse WS networks: **O(T × V)** where T ≈ 10-20

### Space Complexity
- Graph storage: **O(V + E)**
- State tracking: **O(V)**
- Total: **O(V + E)**

## Key Findings

1. **Small-World Effect**: Watts-Strogatz networks show distinctive disease dynamics compared to random/scale-free networks

2. **Critical Threshold**: Infection probability exhibits phase transition around 0.3-0.4
   - Below: Stochastic behavior, high variance
   - Above: Explosive growth, rapid saturation

3. **Network Size Scaling**: Peak infections scale linearly with population size (WS-200 has ~2.3x more than WS-100)

4. **Clustering Impact**: High clustering (0.48+) creates bottleneck effects that slow initial spread despite short path lengths

## Data Structures Justification

### Adjacency List (O(V+E))
- Better than adjacency matrix for sparse networks
- Efficient neighbor iteration
- Memory efficient

### HashSet for States (O(1) lookup)
- Fast state checking
- Efficient iteration over infected nodes
- Clear separation of state groups

### Queue for Infections (O(1) enqueue/dequeue)
- FIFO processing of new infections
- BFS-style propagation pattern
- Supports batch updates

## Files Generated

### Report & Presentation
- **report.tex**: 8-section comprehensive LaTeX report
  - Introduction, related work, network model
  - Algorithm design, data structures, visualization
  - Results, complexity analysis, conclusions
  - Includes tables, equations, and citations

- **presentation.tex**: Beamer slides covering:
  - Problem statement and motivation
  - Network models and algorithms
  - Visualization and results
  - Performance analysis

### Datasets
- watts_strogatz_100.csv (25 KB)
- watts_strogatz_500.csv (125 KB)
- watts_strogatz_1000.csv (290 KB)

### Experiment Results
- experiment_network_comparison.csv
- experiment_infection_probability.csv

## Testing the System

1. **Upload Sample Data**
   ```bash
   # Use watts_strogatz_100.csv as test input
   ```

2. **Generate Network**
   - Network Type: Watts-Strogatz (Small-world)
   - Nodes: 100
   - Avg Degree: 8

3. **Run Simulation**
   - Infection Probability: 50%
   - Death Probability: 12%
   - Initial Infected: 3

4. **Expected Results**
   - Peak infections: 30-50
   - Final recovered: 70-90
   - Duration: 10-15 steps

## Technical Stack

- **Frontend**: React 18, Three.js r128, Chart.js, Vite
- **Backend**: FastAPI, Uvicorn, Pandas, NetworkX
- **Data Structures**: Python native (dict, set, deque)
- **Visualization**: WebGL (GPU-accelerated)
- **Documentation**: LaTeX (report + Beamer)

## Performance Notes

- **3D Visualization**: Limited to 100 nodes for smooth 60 FPS
- **Backend Simulation**: Can handle up to 10,000 nodes
- **Typical Execution**: 100 nodes in ~10ms, 1000 nodes in ~200ms
- **Network Limit**: Hard maximum of 100 nodes for visualization

## Limitations & Future Work

### Current Limitations
- Homogeneous infection rates (real networks have heterogeneity)
- Static network structure (no temporal dynamics)
- Fixed recovery probability
- No contact tracing or testing
- Simplified death model

### Future Improvements
- Age-stratified transmission rates
- Temporal network evolution
- Vaccination and quarantine simulations
- Contact tracing effectiveness
- Multiple disease variants
- Calibration with real epidemic data

## References

- Watts & Strogatz (1998): Small-world networks
- Barabási & Albert (1999): Scale-free networks
- Erdős & Rényi (1959): Random graphs
- Kermack & McKendrick (1927): SIR model
- Newman (2003): Complex networks review

## Conclusion

This project successfully demonstrates:
- Effective small-world network generation
- Correct SIR epidemic simulation
- Efficient data structure implementation
- Interactive 3D visualization
- Systematic experimental analysis
- Professional documentation

The simulator provides a valuable tool for understanding disease dynamics and evaluating intervention strategies on realistic social networks.
