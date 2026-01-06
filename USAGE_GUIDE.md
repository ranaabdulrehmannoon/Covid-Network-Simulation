# COVID Network Simulator - Usage Guide

## Quick Start

### Prerequisites
- Python 3.8+ with pip
- Node.js 14+ with npm
- Modern web browser (Chrome, Firefox, Safari, Edge)

---

## Installation & Setup

### Step 1: Start the Backend
Open Terminal/PowerShell in the `backend` directory:

```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

```bash
# macOS/Linux
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

✅ You should see: `Uvicorn running on http://127.0.0.1:8000`

---

### Step 2: Start the Frontend
Open a NEW Terminal/PowerShell in the `frontend` directory:

```bash
npm install  # Only needed first time
npm run dev
```

✅ You should see: `Local: http://localhost:5173`

---

### Step 3: Open Application
Click the link or open browser to: **http://localhost:5173**

---

## Using the Application

### Step 1: Upload Your Dataset 📊

1. **Click the upload area** (or drag & drop a CSV file)
2. Select `sentimentdataset.csv` or your own CSV
3. **Wait for green success indicator** - shows ✓ "File loaded successfully"
4. Displays: filename, row count, columns

**Dataset Requirements:**
- Must have a `User` column (required)
- Recommended columns: `Timestamp`, `Country`, `Hashtags`, `Text`

---

### Step 2: Build Network 🔗

1. **Choose a method**:
   - **Co-presence (Social)** (recommended for social data): Groups users by location + time
   - **Hashtag Shared**: Groups users by shared hashtags
   - **Text Similarity**: Groups users by semantic similarity
   - **Edge List (Direct)** (recommended for network data): Uses direct edges from FromNodeId → ToNodeId

2. **Click "Build network"** button
3. **Wait for completion** - Status shows "Network built: X nodes, Y edges"
4. **Graph appears** with animated nodes

---

### Step 3: Configure Simulation ⚙️

1. **Set Initial Infected**:
   - Number of nodes to start infected
   - Recommended: 3-10 nodes
   - Example: 5 for 500-node network

2. **Set Infection Probability** (Slider):
   - How likely disease spreads on contact
   - 0% = no transmission
   - 50% = moderate spread (default)
   - 100% = always transmits
   - For realistic simulation: 30-60%

3. **Set Death Probability** (Slider):
   - Fatality rate for infected
   - 0% = no deaths
   - 12% = realistic COVID (default)
   - 50% = severe disease
   - Common values: 1-15%

---

### Step 4: Run Simulation ▶️

1. **Click "▶ Run simulation"**
2. **Watch the magic happen**:
   - 🔵 Blue nodes = Susceptible (healthy)
   - 🔴 Red nodes = Infected (spreading)
   - 🟢 Green nodes = Recovered (immune)
   - ⚫ Gray nodes = Dead

3. **Monitor real-time updates**:
   - 📍 Status bar shows current step
   - 📊 SIR Table updates with counts & percentages
   - 📈 Line chart shows progression

4. **Stop anytime** with "⏹ Stop" button

5. **Simulation auto-stops** when:
   - All nodes recovered or dead
   - Maximum 10,000 steps reached

---

## Understanding the Visuals

### Network Graph 🕸️
- **Nodes**: Represent people in the social network
- **Lines**: Connections between people (edge probability of transmission)
- **Colors**: Current infection state (see legend)
- **Movement**: Nodes slowly drift and bounce - simulating physical interactions
- **Glow**: Brighter glow = more active disease state

**Zoom Controls**:
- **−** : Zoom out
- **+** : Zoom in
- **⟳** : Reset to 80% zoom
- Shows current zoom level (e.g., "80%")

---

### SIR Statistics Table 📊
**Current snapshot of disease state:**

| Field | Meaning |
|-------|---------|
| **Susceptible (S)** | Healthy nodes (can get infected) |
| **Infected (I)** | Active cases (spreading disease) |
| **Recovered (R)** | Immune nodes (can't get reinfected) |
| **Dead (D)** | Deaths from disease |
| **Total** | Sum of all nodes |

**Percentages** show % of population in each state.

**Color indicators** on left border match node colors.

---

### SIR Dynamics Chart 📈
**Line graph showing disease progression over time:**

- **X-axis**: Simulation step (time)
- **Y-axis**: Number of people
- **Blue line (S)**: Decreases as susceptible get infected
- **Red line (I)**: Peaks when most infected, drops after
- **Green line (R)**: Increases as people recover
- **Gray line (D)**: Increases with deaths

**Peak Infection**: Point where red line is highest

**Flattening Curve**: Lower peak = slower spread (goal of social distancing)

---

### Status Bar 📍
**Real-time feedback on simulation progress:**

- **Color indicators**:
  - 🔵 Blue = Ready/Information
  - 🟡 Yellow = Loading/Running
  - 🟢 Green = Success
  - 🔴 Red = Error

- **Status messages** show:
  - Current step (e.g., "Step 45/200")
  - Live population counts
  - Messages like "✓ File uploaded successfully"

---

## Example Scenario

### Scenario: Office Outbreak
**Setup:**
- 50-person office network (CSV with co-presence data)
- Initial infected: 2 (one visitor/patient zero)
- Infection probability: 40% (masked, distanced office)
- Death probability: 5% (healthy workforce)

**Expected Result:**
- Peak infection in steps 15-25
- ~70% office gets infected
- ~3-4 deaths
- Most recover within 50-60 steps

### Scenario: High-Transmission Disease
**Setup:**
- Same 50-person network
- Initial infected: 1
- Infection probability: 80% (highly contagious)
- Death probability: 2% (asymptomatic spread)

**Expected Result:**
- Rapid spread to 80-90% population
- Peak infection in steps 5-10
- Many more infected but fewer deaths
- All over within 30-40 steps

---

## Tips & Tricks

### 🚀 For Better Performance
- With large networks (1000+ nodes), zoom out to 60% for smooth animation
- Run simulation in modern Chrome/Firefox for best performance
- Close other browser tabs if experiencing lag

### 🔍 For Interesting Results
- **Test different infection rates**: 20%, 50%, 80%
- **Vary initial infected**: Try 1 vs 10 vs 50 nodes
- **Compare methods**: Upload same file, build with different methods
- **Multiple runs**: Stop and run again with same file (random initial selection)

### 📊 For Analysis
- **Note peak infection**: When is red line highest? Why?
- **Compare curves**: Which parameter has bigger impact?
- **Calculate R-value**: How many people does each infected person infect?
- **Estimate mortality**: Final D / Total initial population

### 🔄 Troubleshooting
- If graph looks empty: Try zooming out (−)
- If colors not changing: Wait longer or increase infection probability
- If slow: Reduce zoom level or test with smaller dataset
- If error: Check backend is running on port 8000

---

## Advanced: Using Your Own Data

### CSV Format Preparation

**For Edge List Method** (Direct network connections):
```csv
FromNodeId,ToNodeId
30,1412
30,3352
3,28
3,30
1412,5254
```
- Each row is an edge between two nodes
- FromNodeId: Source node
- ToNodeId: Destination node
- No duplicates needed (graph is undirected)
- Works with numeric or string node IDs

**For Co-presence Method:**
```csv
User,Timestamp,Country
alice,2023-01-15 12:30,USA
bob,2023-01-15 12:35,USA
carol,2023-01-15 13:00,USA
```

**For Hashtag Method:**
```csv
User,Hashtags
alice,#news #covid #health
bob,#health #science
```

**For Text Similarity Method:**
```csv
User,Text
alice,"COVID cases rising in our city"
bob,"Health officials warn of new variant"
```

### Network Method Selection
- **Edge List (Direct)**: Use when you have pre-computed network edges (fastest, most direct)
- **Co-presence**: Use when you have time + location data (derives edges from co-occurrence)
- **Hashtag**: Use when you have social media hashtags
- **Text**: Use when you have message/tweet content

---

## Understanding the Science

### SIR Model Basics
The **Susceptible-Infected-Recovered** (SIR) model:

```
Susceptible → Infected → Recovered
                  ↓
                 Dead
```

- **Susceptible (S)**: Can catch disease
- **Infected (I)**: Has disease, can spread it
- **Recovered (R)**: Had disease, now immune
- **Dead (D)**: Died from disease

### Key Metrics
- **R₀ (Basic Reproduction Number)**: Avg people infected by 1 sick person
  - Calculated as: peak I nodes / initial I nodes
  - R₀ > 1: Disease spreads
  - R₀ < 1: Disease dies out

- **Attack Rate**: % of population that gets infected
  - = (Total infected during outbreak) / (Total population) × 100%

- **Case Fatality Rate**: % of infected who die
  - = (Total dead) / (Total infected) × 100%

---

## Keyboard Shortcuts
- **None implemented yet** - All controls are buttons/sliders

---

## File Information

### sample-data.csv
Included dataset with:
- 733 social media posts
- Users from multiple countries
- Timestamps from January 2023
- Sentiments and engagement metrics
- Hashtags and platform info

---

## Getting Help

### Common Issues

**Q: "No graph built" error**
A: You must click "Build network" after uploading CSV

**Q: Graph visualization empty**
A: Try zooming out (−) or check if network was built successfully

**Q: Simulation not starting**
A: Ensure graph is built AND set initial infected > 0

**Q: Nodes not changing colors**
A: Increase infection probability to 50%+ for more obvious spread

**Q: Browser freezes**
A: Pause tab in Chrome devtools, reduce network size, or close other tabs

---

## Feedback & Improvements

Current features:
- ✅ Real-world social network data
- ✅ Multiple network construction methods
- ✅ Animated network visualization
- ✅ SIR simulation with death state
- ✅ Real-time statistics & charts
- ✅ Configurable disease parameters
- ✅ Professional UI/UX

Future ideas:
- 3D graph visualization
- Network analysis metrics
- Intervention simulations (vaccination, lockdown)
- Parameter sensitivity analysis
- Export results as PDF/PNG

---

**Enjoy exploring disease dynamics! 🦠→🛡️**
