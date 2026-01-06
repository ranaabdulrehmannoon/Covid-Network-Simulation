# 3D Network Visualization Guide

## Overview
The COVID Network Simulator now features a stunning **3D network visualization** using Three.js. The network displays nodes as interactive 3D spheres with realistic physics-based movement that is very slow and gentle.

---

## Features

### 3D Visualization
- **3D Scene**: Full 3D space with X, Y, Z coordinates
- **Spherical Nodes**: Each node is a 3D sphere
- **Dynamic Edges**: Lines connecting related nodes, updating in real-time
- **Color-Coded States**:
  - 🔵 **Blue (#667eea)**: Susceptible nodes
  - 🔴 **Red (#ff6b6b)**: Infected nodes
  - 🟢 **Green (#51cf66)**: Recovered nodes
  - ⚫ **Gray (#6c757d)**: Dead nodes

### Physics-Based Movement
- **Very Slow**: Gentle drift with minimal velocity (0-0.8 units/frame)
- **Smooth Animation**: Continuous real-time update at 60 FPS
- **Attractive Forces**: Nodes gently drift toward center
- **Boundary Collision**: Bounce off world boundaries with damping

### Interactive Controls
- **Drag to Rotate**: Click and drag to manually rotate the scene
- **Scroll to Zoom**: Mouse wheel adjusts camera distance
- **Auto-Rotation**: Scene slowly auto-rotates when not dragging
- **Responsive**: Adapts to window resize

### Performance
- **Maximum Nodes**: 100 (enforced for smooth performance)
- **Real-time Updates**: State changes reflected instantly
- **Optimized**: GPU-accelerated rendering via WebGL
- **Smooth**: 60 FPS animation on modern hardware

---

## How It Works

### Scene Setup
```javascript
1. Three.js Scene with dark background (#0f172a)
2. PerspectiveCamera positioned at z=50
3. WebGLRenderer with antialiasing enabled
4. DirectionalLight + AmbientLight for proper shading
```

### Node Physics
```
For each node each frame:
1. Update velocity based on:
   - Random fluctuation (Brownian motion)
   - Attractive force toward center (0.0004x acceleration)
2. Apply speed limits (-0.8 to +0.8 units)
3. Update position
4. Bounce at boundaries (±40 units)
5. Update mesh position in 3D space
```

### Edge Updates
```
For each edge each frame:
1. Get current node positions
2. Update line geometry endpoints
3. Mark geometry as needing update
4. Render updated line in next frame
```

### Auto-Rotation
```
If user not dragging:
- Rotate scene around X axis: +0.0001 rad/frame
- Rotate scene around Y axis: +0.0002 rad/frame
- Very slow rotation for cinematic effect
```

---

## Physics Parameters

### Node Movement
| Parameter | Value | Effect |
|-----------|-------|--------|
| Random fluctuation | 0.08 | Brownian motion amplitude |
| Attraction strength | 0.0004 | Pull toward center |
| Max velocity | 0.8 | Speed limit per axis |
| Boundary position | ±40 units | World limits |
| Bounce damping | 0.8 | Restitution coefficient |

### Animation
| Parameter | Value | Effect |
|-----------|-------|--------|
| FPS Target | 60 | Frame rate |
| Auto-rotate X | 0.0001 rad/frame | ~9 min full rotation |
| Auto-rotate Y | 0.0002 rad/frame | ~4.5 min full rotation |
| Node radius | 1.5 units | Visual size |
| Max nodes | 100 | Performance limit |

---

## Implementation Details

### Three.js Components

**Geometry**:
- `SphereGeometry(1.5, 32, 32)` - Node mesh with 32 segments

**Materials**:
- `MeshPhongMaterial` - Nodes with realistic lighting
- `LineBasicMaterial` - Edges

**Lighting**:
- DirectionalLight: 0.8 intensity from (50, 50, 50)
- AmbientLight: 0.5 intensity for fill light
- Enables proper 3D visualization with shading

**Camera**:
- Type: PerspectiveCamera (75° FOV)
- Position: (0, 0, 50)
- Zoom range: 10-150 units

### State Synchronization
```javascript
When simulation updates:
1. New graph data arrives via `/graph` endpoint
2. Component updates dataRef.current
3. Animation loop reads currentData
4. Node states compared with previous
5. Material colors updated if state changed
6. Physics continues smoothly
```

### Memory Management
```javascript
On cleanup:
1. Stop animation loop
2. Remove event listeners
3. Remove canvas from DOM
4. Dispose renderer (GPU memory)
5. Allows garbage collection
```

---

## Interaction Guide

### Rotating the View
1. **Click and drag** the 3D network with mouse
2. Auto-rotation pauses while dragging
3. Release to resume auto-rotation
4. Rotation speed: ~9 minutes per full X rotation

### Zooming
1. **Scroll up** to zoom in (camera closer)
2. **Scroll down** to zoom out (camera farther)
3. Zoom range: 10-150 units from origin
4. Smooth transition

### Resetting View
1. Wait 2 seconds after last drag (auto-rotation resumes)
2. Or refresh the page for default view

---

## Visual Design

### Color Palette
```
Scene Background: #0f172a (dark blue)
Susceptible (S):  #667eea (indigo)
Infected (I):     #ff6b6b (red)
Recovered (R):    #51cf66 (green)
Dead (D):         #6c757d (gray)
Edges:            #475569 (slate)
```

### Lighting
- **Directional Light**: Creates depth and shadows
- **Ambient Light**: Prevents completely dark areas
- **Phong Material**: Realistic specular highlights

### Legend
Displays below 3D visualization:
- Color code for each state
- User instructions (Drag to rotate, Scroll to zoom)
- Responsive and accessible

---

## Node Limit: 100 Nodes

### Why 100?
- **Performance**: Maintains 60 FPS on mid-range hardware
- **Visibility**: All nodes visible and interactive at once
- **Interactivity**: Responsive to user input
- **Simulation**: Complete visualization of disease spread

### What Happens if Network > 100?
```
Frontend (React):
- Error displayed in status bar
- Status: "❌ Network too large (max 100 nodes)"

Backend (FastAPI):
- /graph endpoint returns error
- Error message: "Network too large: X nodes (max 100)"
```

### How to Use Large Networks
**Option 1: Sample the Network**
```python
import networkx as nx
G_large = nx.read_graphml('large_network.graphml')
G_sample = nx.subgraph(G_large, list(G_large.nodes())[:100])
```

**Option 2: Use Different Method**
- Try edgelist method which may remove isolates
- Co-presence method creates sparse networks

**Option 3: Filter by Degree**
```python
# Keep only high-degree nodes
nodes = [n for n, d in G.degree() if d >= 2]
G_filtered = G.subgraph(nodes)
```

---

## Performance Optimization

### Hardware Requirements
**Minimum**:
- GPU: WebGL 2.0 support
- RAM: 256MB free
- CPU: Modern multi-core

**Recommended**:
- GPU: Dedicated graphics card
- RAM: 1GB+
- CPU: i5 or better

### Optimization Tips
1. **Close browser tabs**: Reduce memory contention
2. **Update drivers**: Ensure GPU drivers are current
3. **Reduce other applications**: Free system resources
4. **Use modern browser**: Chrome/Firefox have best WebGL

### Troubleshooting

**Problem: Low FPS**
- Solution: Reduce number of nodes
- Or: Close other applications
- Or: Update graphics drivers

**Problem: Scene appears black**
- Solution: Check if WebGL is enabled
- Or: Try different browser
- Or: Update graphics drivers

**Problem: Nodes moving too fast**
- Solution: This indicates high FPS (good!)
- Or: Can't be changed without recompile

---

## Technical Specifications

### Dependencies
- **three.js** r128: 3D graphics library
- **react** 18.2.0: UI framework
- **chart.js**: Separate 2D charts component

### Rendering
- **WebGLRenderer**: GPU-accelerated
- **Antialias**: Enabled for smooth edges
- **Pixel Ratio**: Adapts to device (Retina support)

### Scene Graph
```
Scene
├── Directional Light
├── Ambient Light
├── Node Meshes (up to 100)
│   ├── SphereGeometry
│   └── MeshPhongMaterial
└── Edge Lines (up to ~500)
    ├── BufferGeometry
    └── LineBasicMaterial
```

### Frame Rate Management
- **Target**: 60 FPS
- **Automatic**: `requestAnimationFrame` handles timing
- **Adaptive**: Slows naturally if system can't keep up

---

## Comparison: 2D vs 3D

### 2D Canvas (Old)
- Flat visualization
- Limited interaction
- Slower physics (more collisions)
- Easier on older hardware

### 3D WebGL (New) ✨
- Full 3D space
- Rich interaction (rotate, zoom)
- Smooth physics (3D forces)
- Requires modern hardware
- More visually impressive
- Better for complex networks

---

## Future Enhancements

1. **Force-Directed Layout**
   - Implement Barnes-Hut algorithm
   - Better initial positioning
   - Automatic layout computation

2. **Node Labels**
   - Display node IDs on click
   - Billboarded text (always faces camera)
   - Search/highlight functionality

3. **Particle Effects**
   - Infection spread visualization
   - Recovery particles
   - Death animations

4. **Advanced Controls**
   - Double-click to focus on node
   - Right-click context menu
   - Keyboard shortcuts

5. **Export Functionality**
   - Screenshot (WebGL to canvas to PNG)
   - Video recording (3D animation)
   - Network statistics

6. **Multi-View**
   - Side-by-side comparison
   - Timeline scrubbing
   - Parameter exploration

---

## Browser Compatibility

| Browser | WebGL 2.0 | Status |
|---------|-----------|--------|
| Chrome | ✅ | Excellent |
| Firefox | ✅ | Excellent |
| Safari | ✅ | Good |
| Edge | ✅ | Good |
| IE 11 | ❌ | Not supported |

---

## Debugging

### Enable Three.js Stats
```javascript
// Add to App.jsx if debugging
import Stats from 'three/examples/jsm/libs/stats.module.js'
const stats = new Stats()
document.body.appendChild(stats.dom)
// In animation loop: stats.update()
```

### Check WebGL Status
```javascript
const canvas = document.createElement('canvas')
const gl = canvas.getContext('webgl2')
console.log('WebGL2 supported:', gl !== null)
```

### Monitor Performance
- Open DevTools (F12)
- Performance tab
- Record animation
- Check GPU usage and frame timing

---

## Key Files

- `frontend/src/App.jsx` - Network3D component
- `frontend/src/styles.css` - 3D styling
- `frontend/package.json` - three.js dependency
- `backend/app/main.py` - 100-node validation

---

**Ready to explore the 3D network simulation! 🚀**
