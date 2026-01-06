# COVID Network Simulator - Implementation Summary

## Overview
A professional web-based COVID-19 spread simulation system with real-world social network data, interactive visualization, and SIR (Susceptible-Infected-Recovered) dynamics tracking with death state.

---

## Key Features Implemented

### 1. **File Upload with Success Indication**
- **Green success state**: Upload area turns green (#22c55e) when file is successfully loaded
- Shows filename, row count, and column count
- "Clear & Upload New" button to reset and load different dataset
- Real-time feedback with descriptive status messages

### 2. **Network Building from Real-World Data**
- Supports four network construction methods:
  - **Co-presence (Social)**: Groups users by geographic location and timestamp (Country, Year, Month, Day, Hour)
  - **Hashtag Shared**: Creates network based on shared hashtag interactions
  - **Text Similarity**: Uses TF-IDF vectorizer for semantic similarity (requires scikit-learn)
  - **Edge List (Direct)**: Directly reads edge connections from `FromNodeId` and `ToNodeId` columns
- Automatic removal of isolated nodes
- Spring layout algorithm for force-directed graph visualization

### 3. **Real-Time Animated Network Visualization**
- **2D Canvas-based visualization** with:
  - Smooth node movement and interactions
  - Color-coded node states:
    - 🔵 **Susceptible (S)**: Blue (#667eea) - uninfected
    - 🔴 **Infected (I)**: Red (#ff6b6b) - actively spreading
    - 🟢 **Recovered (R)**: Green (#51cf66) - immune
    - ⚫ **Dead (D)**: Gray (#6c757d) - deceased
  - Realistic physics simulation with velocity damping and wall bouncing
  - Glow effects around nodes for better visibility
  - Edge visualization showing network connections
  - Zoom controls (0.5x to 1.5x magnification)

### 4. **Simulation Controls with Probability Parameters**
- **Initial Infected Nodes**: Configurable starting infected population (default: 3)
- **Infection Probability Slider**: 0-100% transmission likelihood per contact (default: 50%)
- **Death Probability Slider**: 0-100% fatality rate for infected (default: 12%)
- Parameters are disabled during active simulation for consistency
- Real-time probability value display with percentage

### 5. **SIR Statistics Dashboard**
- Professional HTML table showing current state:
  - State count and percentage distribution
  - Clear status descriptions
  - Color-coded rows with left border indicators
  - Total population summary row
  - Responsive hover effects
- Displays latest snapshot from simulation history

### 6. **SIR Dynamics Chart**
- **Line graph** showing disease progression over time
- Four data series:
  - Susceptible (S) - blue line
  - Infected (I) - red line
  - Recovered (R) - green line
  - Dead (D) - gray line
- Interactive chart.js visualization with:
  - Smooth bezier curves (tension: 0.4)
  - Data points with hover information
  - Semi-transparent fill areas under each line
  - Professional legend and tooltips
  - Grid and axis labels

### 7. **Real-Time Status Bar**
- **Color-coded status indicators** (no rotating animation):
  - 🔵 Blue: Ready/Info state
  - 🟡 Yellow: Loading state
  - 🔴 Red: Error state
  - 🟢 Green: Success state
- Live step counter: "Step X/Y"
- Real-time population breakdown: "S: X | I: Y | R: Z | D: W"
- Clear status messages describing current operation

### 8. **Simulation Control**
- **Start Button**: Begins simulation with configured parameters
- **Stop Button**: Pauses simulation during execution
- Auto-completion when all nodes are recovered or dead
- Animated step-by-step progression (300ms per step)
- Graceful error handling with descriptive messages

### 9. **Professional UI/UX Design**
- **Dark theme** with indigo/purple accent colors
- **Responsive layout**: 
  - Desktop: 2-column (controls sidebar + workspace)
  - Tablet/Mobile: Single column
- **Smooth animations**:
  - Fade-in effects with staggered timing
  - Button scale and hover effects
  - Slider thumb animations
- **Accessibility**:
  - Clear visual hierarchy
  - Sufficient color contrast
  - Disabled states properly indicated

---

## Technical Architecture

### Frontend (React + Vite)
**Components:**
- `NetworkCanvas`: 2D canvas-based graph renderer with physics simulation
- `SIRStatsTable`: Statistics table component
- `App`: Main application orchestrator

**State Management:**
- React hooks for UI state
- Local file info and simulation history tracking
- Real-time graph updates via async polling

**Styling:**
- CSS Grid for responsive layouts
- CSS custom properties for theming
- Smooth transitions and animations

**External Libraries:**
- `chart.js` & `react-chartjs-2`: Graph visualization
- `axios`: API communication

### Backend (FastAPI + NetworkX)
**Endpoints:**
- `POST /upload-csv`: File upload and validation
- `POST /build-network`: Network construction from data
- `POST /simulate`: Run SIR simulation
- `GET /graph`: Retrieve current graph state
- `POST /generate-network`: Generate synthetic graphs
- `GET /download/graph`: Export graph for analysis

**Simulator Module:**
- `build_network_from_df()`: Constructs graphs from real data
- `reset_states()`: Initializes node states with infection probability
- `simulate_sir_realtime()`: Runs step-by-step SIR simulation
- `graph_to_json()`: Serializes graph for frontend

---

## Network Construction Algorithms

### Edge List Method (Recommended for Pre-computed Networks)
```
Input: CSV with FromNodeId, ToNodeId columns
Output: NetworkX Graph

Process:
1. Read CSV file
2. For each row:
   - Extract FromNodeId and ToNodeId
   - Add edge between nodes to graph
3. Remove isolated nodes
4. Compute spring layout for visualization

Complexity:
- Time: O(E) where E = number of edges
- Space: O(N + E) where N = number of nodes
- Layout: O(N * iterations) ≈ O(N²) for typical graphs
```

### Co-presence Method
```
Input: CSV with User, Timestamp, Country columns
Output: NetworkX Graph

Process:
1. Parse timestamps
2. Group by (Country, Year, Month, Day, Hour)
3. For each group, connect all user pairs
4. Remove isolated nodes
5. Compute spring layout

Complexity:
- Time: O(T * U² * H) where T = time periods, U = users/period, H = height of groups
- Space: O(N + E)
- Results in dense local clusters connected sparsely
```

### Hashtag Method
```
Input: CSV with User, Hashtags columns
Output: NetworkX Graph (bipartite projection)

Process:
1. Create bipartite graph (users, hashtags)
2. Add edges between users and their hashtags
3. Project to user graph (users connected if sharing tags)
4. Remove isolated nodes
5. Compute spring layout

Complexity:
- Time: O(U * T) where U = users, T = tags per user
- Space: O(N + E)
- Results in cliques of co-tagging users
```

### Text Similarity Method
```
Input: CSV with User, Text columns
Output: NetworkX Graph

Process:
1. Vectorize texts using TF-IDF
2. Compute cosine similarity matrix (all pairs)
3. Connect users if similarity > 0.45 threshold
4. Remove isolated nodes
5. Compute spring layout

Complexity:
- Time: O(U² * D) where U = users, D = document dimension
- Space: O(N + E + D*U) for vectors
- Results in semantic-based clusters
```

---

## Algorithm: SIR Disease Spread

### Model Description
**Compartmental Model** with four states:

1. **Susceptible (S)**: Can contract disease on contact with infected
2. **Infected (I)**: Actively spreads disease through network edges
3. **Recovered (R)**: No longer infectious, gains immunity
4. **Dead (D)**: Disease fatality outcome

### Spread Mechanism
Each simulation step:
1. **For each infected node (I)**:
   - Check death probability: if `random() < death_prob` → transition to Dead (D)
   - Check recovery probability: if `random() < recovery_prob` → transition to Recovered (R)
   - For each susceptible neighbor:
     - If `random() < infection_prob` → transition neighbor to Infected (I)

2. **Termination**: Stops when no susceptible or infected nodes remain

### Probability Parameters
- **infection_prob**: Per-edge transmission likelihood (set during reset_states)
- **recovery_prob**: Per-node recovery rate (randomized 0.3-0.9)
- **death_prob**: Mortality rate for infected nodes

### Complexity Analysis
- **Time**: O(steps × nodes × edges)
  - steps ≤ 10,000 (safety limit)
  - Typically converges in 100-300 steps
- **Space**: O(nodes + edges) for graph storage + O(steps) for history

---

## Data Flow

```
CSV File Upload
    ↓
[Upload Endpoint]
    ↓
DataFrame parsed & stored
    ↓
Build Network (Choose Method)
    ↓
[Build Network Endpoint]
    ↓
NetworkX Graph created
    ↓
Force-directed layout computed
    ↓
Graph displayed (Canvas with animation)
    ↓
Run Simulation (Set probabilities)
    ↓
[Simulate Endpoint]
    ↓
Initial infected nodes set to state "I"
    ↓
Step-by-step simulation loop
    ↓
Each step: Graph fetched, visualized, history recorded
    ↓
SIR Table & Chart updated in real-time
    ↓
Simulation stops when equilibrium reached
    ↓
Final statistics displayed
```

---

## Usage Instructions

### 1. **Start Backend**
```bash
cd backend
python -m venv .venv
# Windows:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. **Start Frontend**
```bash
cd frontend
npm install
npm run dev
```

### 3. **Use Application**
1. **Upload Dataset**:
   - Drag CSV file or click to select
   - File must contain "User" and optionally "Timestamp" columns
   - Wait for green success state

2. **Build Network**:
   - Select method (copresence recommended for social data)
   - Click "Build network"
   - Wait for graph visualization to appear

3. **Configure Simulation**:
   - Set initial infected count (e.g., 3-5)
   - Adjust infection probability (0-100%)
   - Adjust death probability (0-100%, default 12%)

4. **Run Simulation**:
   - Click "▶ Run simulation"
   - Watch network nodes change colors as disease spreads
   - Monitor SIR statistics table and chart in real-time
   - Click "⏹ Stop" to pause at any time

---

## Dataset Requirements

### Format-Specific Requirements:

**Edge List Method** (Recommended for network data):
- `FromNodeId`: Source node identifier
- `ToNodeId`: Destination node identifier
- Works with numeric or string IDs
- Example: `network_edgelist_example.csv`

**Social Data Methods**:
- Minimum: `User` column (user/node identifier)

**Co-presence Method**:
- Required: `User` column
- Recommended: `Timestamp` (DateTime), `Country` (or any grouping column)

**Hashtag Method**:
- Required: `User`, `Hashtags` (space or comma-separated)

**Text Similarity Method**:
- Required: `User`, `Text` (content for similarity)

### Example Datasets (Included):

**sentimentdataset.csv**:
- 733 rows of social media data
- Use with: Co-presence, Hashtag, or Text methods
- Columns: Text, Sentiment, Timestamp, User, Platform, Hashtags, Country, etc.

**network_edgelist_example.csv**:
- Edge list format with direct connections
- Use with: Edge List (Direct) method
- Columns: FromNodeId, ToNodeId

---

## Color Scheme

| State | Color | Hex Code | Meaning |
|-------|-------|----------|---------|
| Susceptible | Blue | #667eea | Healthy, can be infected |
| Infected | Red | #ff6b6b | Actively spreading disease |
| Recovered | Green | #51cf66 | Immune after recovery |
| Dead | Gray | #6c757d | Lost to disease |

---

## Performance Considerations

- **Network Size**: Tested with 100-1000 nodes
  - Larger networks (5000+) may experience slower visualization
  - Simulation remains fast due to efficient loop structure
  
- **Simulation Speed**: Step duration = 300ms
  - Adjustable in `handleSim()` function if needed
  - Total runtime = steps × 300ms (typically 30-90 seconds)

- **Browser**: Works on modern browsers (Chrome, Firefox, Safari, Edge)
  - Canvas rendering is hardware-accelerated
  - Smooth 60 FPS animation target

---

## Future Enhancements

1. **3D Visualization**: WebGL-based 3D graph rendering
2. **Parameter Sweeping**: Run multiple simulations with different parameters
3. **Export Features**: Download graph, simulation data, charts as images/PDFs
4. **Advanced Models**: SEIR (Exposed), SIRD (with vital statistics), etc.
5. **Network Metrics**: Betweenness, clustering coefficient, community detection
6. **Real-Time Collaboration**: Multiple users viewing same simulation
7. **Mobile Optimization**: Touch controls for mobile devices
8. **Dark/Light Theme Toggle**: User-selectable interface theme

---

## File Structure

```
d:\3rd Semester\Data Structures\DSA Project2\
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI endpoints
│   │   └── simulator.py      # SIR simulation engine
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── api.js           # API client
│   │   ├── styles.css       # Application styling
│   │   └── main.jsx         # React entry point
│   ├── package.json         # NPM dependencies
│   └── index.html           # HTML template
├── sentimentdataset.csv     # Sample dataset
└── IMPLEMENTATION_SUMMARY.md # This file
```

---

## Troubleshooting

**Issue**: "No graph built" error when running simulation
- **Solution**: Build network first with "Build network" button

**Issue**: Nodes not changing colors during simulation
- **Solution**: Ensure graph is built before simulation starts

**Issue**: CORS errors
- **Solution**: Backend CORS middleware is already configured to allow all origins

**Issue**: Slow visualization with large graphs
- **Solution**: Reduce zoom level or consider generating smaller test graph

**Issue**: API connection refused
- **Solution**: Ensure backend is running on http://localhost:8000

---

## Version Information

- **React**: 18+
- **FastAPI**: Latest
- **NetworkX**: 3.0+
- **Python**: 3.8+
- **Node.js**: 14+

---

## License & Attribution

This project implements standard epidemiological SIR models combined with social network analysis for educational purposes.

**Created**: December 2024
**Purpose**: Data Structures Project - Disease Spread Simulation
**Institution**: 3rd Semester DSA Course
