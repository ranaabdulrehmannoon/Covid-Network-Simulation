import React, { useState, useEffect, useRef, useCallback, memo, forwardRef, useImperativeHandle } from 'react'
import { getGraph, simulate, generateNetwork } from './api'
import { Line } from 'react-chartjs-2'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler } from 'chart.js'
import * as THREE from 'three'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler)

const Network3D = memo(forwardRef(({ data, zoom = 1, onStatusUpdate = null, nodeStates = {} }, ref) => {
  const containerRef = useRef(null)
  const sceneRef = useRef(null)
  const cameraRef = useRef(null)
  const rendererRef = useRef(null)
  const nodesRef = useRef({})
  const velocitiesRef = useRef({})
  const edgeLinesRef = useRef([])
  const nodeStatesRef = useRef({})

  useImperativeHandle(ref, () => ({
    updateNodeStates: (newStates) => {
      nodeStatesRef.current = newStates
    }
  }))
  
  const getNodeColor = (state) => {
    switch(state) {
      case 'I': return 0xff6b6b
      case 'R': return 0x51cf66
      case 'D': return 0x6c757d
      default: return 0x667eea
    }
  }
  
  useEffect(() => {
    nodeStatesRef.current = nodeStates
  }, [nodeStates])
  
  useEffect(() => {
    const container = containerRef.current
    if (!container || !data || data.nodes.length === 0) return
    
    if (data.nodes.length > 100) {
      if (onStatusUpdate) onStatusUpdate('❌ Network too large (max 100 nodes)', 'error')
      return
    }
    
    const w = container.clientWidth
    const h = container.clientHeight
    
    const scene = new THREE.Scene()
    scene.background = new THREE.Color(0x0f172a)
    
    const camera = new THREE.PerspectiveCamera(75, w / h, 0.1, 1000)
    camera.position.z = 50
    
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    renderer.setSize(w, h)
    renderer.setPixelRatio(window.devicePixelRatio)
    container.appendChild(renderer.domElement)
    
    sceneRef.current = scene
    cameraRef.current = camera
    rendererRef.current = renderer
    
    const nodeGeometry = new THREE.SphereGeometry(0.6, 32, 32)
    const edgeMaterial = new THREE.LineBasicMaterial({ color: 0x475569, linewidth: 1 })
    
    data.nodes.forEach((n) => {
      const state = nodeStatesRef.current[n.id] || n.state || 'S'
      const material = new THREE.MeshPhongMaterial({ color: getNodeColor(state) })
      const mesh = new THREE.Mesh(nodeGeometry, material)
      const pos = {
        x: (Math.random() - 0.5) * 80,
        y: (Math.random() - 0.5) * 80,
        z: (Math.random() - 0.5) * 80
      }
      mesh.position.set(pos.x, pos.y, pos.z)
      scene.add(mesh)
      
      nodesRef.current[n.id] = {
        mesh: mesh,
        pos: pos,
        state: state
      }
      
      velocitiesRef.current[n.id] = {
        vx: (Math.random() - 0.5) * 0.02,
        vy: (Math.random() - 0.5) * 0.02,
        vz: (Math.random() - 0.5) * 0.02
      }
    })
    
    const light = new THREE.DirectionalLight(0xffffff, 0.8)
    light.position.set(50, 50, 50)
    scene.add(light)
    
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
    scene.add(ambientLight)
    
    data.edges.forEach((e) => {
      const nodeA = nodesRef.current[e.u]
      const nodeB = nodesRef.current[e.v]
      
      if (nodeA && nodeB) {
        const points = [
          new THREE.Vector3(nodeA.pos.x, nodeA.pos.y, nodeA.pos.z),
          new THREE.Vector3(nodeB.pos.x, nodeB.pos.y, nodeB.pos.z)
        ]
        const geometry = new THREE.BufferGeometry().setFromPoints(points)
        const line = new THREE.Line(geometry, edgeMaterial)
        scene.add(line)
        edgeLinesRef.current.push({ line, u: e.u, v: e.v })
      }
    })
    
    let running = true
    let autoRotate = true
    
    function animate() {
      if (!running) return
      
      Object.keys(nodesRef.current).forEach((nodeId) => {
        const nodeObj = nodesRef.current[nodeId]
        const vel = velocitiesRef.current[nodeId]
        const newState = nodeStatesRef.current[nodeId]
        
        if (newState && newState !== nodeObj.state) {
          nodeObj.state = newState
          nodeObj.mesh.material.color.setHex(getNodeColor(newState))
        }
        
        vel.vx += (Math.random() - 0.5) * 0.008 + (0 - nodeObj.pos.x) * 0.00004
        vel.vy += (Math.random() - 0.5) * 0.008 + (0 - nodeObj.pos.y) * 0.00004
        vel.vz += (Math.random() - 0.5) * 0.008 + (0 - nodeObj.pos.z) * 0.00004
        
        vel.vx = Math.max(-0.08, Math.min(0.08, vel.vx))
        vel.vy = Math.max(-0.08, Math.min(0.08, vel.vy))
        vel.vz = Math.max(-0.08, Math.min(0.08, vel.vz))
        
        nodeObj.pos.x += vel.vx
        nodeObj.pos.y += vel.vy
        nodeObj.pos.z += vel.vz
        
        const boundary = 40
        if (nodeObj.pos.x < -boundary) { nodeObj.pos.x = -boundary; vel.vx *= -1 }
        if (nodeObj.pos.x > boundary) { nodeObj.pos.x = boundary; vel.vx *= -1 }
        if (nodeObj.pos.y < -boundary) { nodeObj.pos.y = -boundary; vel.vy *= -1 }
        if (nodeObj.pos.y > boundary) { nodeObj.pos.y = boundary; vel.vy *= -1 }
        if (nodeObj.pos.z < -boundary) { nodeObj.pos.z = -boundary; vel.vz *= -1 }
        if (nodeObj.pos.z > boundary) { nodeObj.pos.z = boundary; vel.vz *= -1 }
        
        nodeObj.mesh.position.set(nodeObj.pos.x, nodeObj.pos.y, nodeObj.pos.z)
      })
      
      edgeLinesRef.current.forEach(({ line, u, v }) => {
        const nodeA = nodesRef.current[u]
        const nodeB = nodesRef.current[v]
        if (nodeA && nodeB) {
          const positions = line.geometry.attributes.position.array
          positions[0] = nodeA.pos.x
          positions[1] = nodeA.pos.y
          positions[2] = nodeA.pos.z
          positions[3] = nodeB.pos.x
          positions[4] = nodeB.pos.y
          positions[5] = nodeB.pos.z
          line.geometry.attributes.position.needsUpdate = true
        }
      })
      
      if (autoRotate) {
        scene.rotation.x += 0.0001
        scene.rotation.y += 0.0002
      }
      
      renderer.render(scene, camera)
      requestAnimationFrame(animate)
    }
    
    const handleMouseMove = (event) => {
      if (event.buttons === 1) {
        autoRotate = false
        const deltaX = event.movementX * 0.005
        const deltaY = event.movementY * 0.005
        scene.rotation.y += deltaX
        scene.rotation.x += deltaY
      }
    }
    
    const handleMouseUp = () => {
      autoRotate = true
    }
    
    const handleMouseWheel = (event) => {
      event.preventDefault()
      camera.position.z += event.deltaY * 0.1
      camera.position.z = Math.max(10, Math.min(150, camera.position.z))
    }
    
    renderer.domElement.addEventListener('mousemove', handleMouseMove)
    renderer.domElement.addEventListener('mouseup', handleMouseUp)
    renderer.domElement.addEventListener('wheel', handleMouseWheel, { passive: false })
    
    const handleResize = () => {
      const newW = container.clientWidth
      const newH = container.clientHeight
      camera.aspect = newW / newH
      camera.updateProjectionMatrix()
      renderer.setSize(newW, newH)
    }
    
    window.addEventListener('resize', handleResize)
    
    animate()
    
    return () => {
      running = false
      renderer.domElement.removeEventListener('mousemove', handleMouseMove)
      renderer.domElement.removeEventListener('mouseup', handleMouseUp)
      renderer.domElement.removeEventListener('wheel', handleMouseWheel)
      window.removeEventListener('resize', handleResize)
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement)
      }
      renderer.dispose()
    }
  }, [data])
  
  return (
    <>
      <div ref={containerRef} style={{width: '100%', height: '600px'}} />
      <div className="legend">
        <div className="legend-item">
          <div className="legend-color" style={{backgroundColor: '#667eea'}}></div>
          <span>Susceptible (S)</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{backgroundColor: '#ff6b6b'}}></div>
          <span>Infected (I)</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{backgroundColor: '#51cf66'}}></div>
          <span>Recovered (R)</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{backgroundColor: '#6c757d'}}></div>
          <span>Dead (D)</span>
        </div>
        <div className="legend-item" style={{fontSize: '12px', color: '#94a3b8', marginTop: '8px', width: '100%'}}>
          <span>💡 Drag to rotate | Scroll to zoom</span>
        </div>
      </div>
    </>
  )
}))

export default function App(){
  const [graph, setGraph] = useState(null)
  const [history, setHistory] = useState([])
  const [status, setStatus] = useState('Ready')
  const [statusType, setStatusType] = useState('info')
  const [loading, setLoading] = useState(false)
  const [zoom, setZoom] = useState(0.8)
  const [infectionProb, setInfectionProb] = useState(0.5)
  const [deathProb, setDeathProb] = useState(0.12)
  const [genMethod, setGenMethod] = useState('watts_strogatz')
  const [nNodes, setNNodes] = useState(100)
  const [avgDegree, setAvgDegree] = useState(8)
  const [nodeStates, setNodeStates] = useState({})
  const nodeStatesRef = useRef({})
  const networkRef = useRef(null)

  function SIRStatsTable({ history }) {
    if (history.length === 0) {
      return (
        <div style={{textAlign: 'center', padding: '20px', color: '#94a3b8'}}>
          No simulation data available
        </div>
      )
    }
    const latestStats = history[history.length - 1]
    const totalNodes = latestStats.S + latestStats.I + latestStats.R + latestStats.D
    
    return (
      <div className="sir-stats-table">
        <table>
          <thead>
            <tr>
              <th>State</th>
              <th>Count</th>
              <th>Percentage</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr className="sir-row susceptible">
              <td>Susceptible (S)</td>
              <td>{latestStats.S}</td>
              <td>{totalNodes > 0 ? ((latestStats.S / totalNodes) * 100).toFixed(1) : 0}%</td>
              <td>Not infected</td>
            </tr>
            <tr className="sir-row infected">
              <td>Infected (I)</td>
              <td>{latestStats.I}</td>
              <td>{totalNodes > 0 ? ((latestStats.I / totalNodes) * 100).toFixed(1) : 0}%</td>
              <td>Spreading virus</td>
            </tr>
            <tr className="sir-row recovered">
              <td>Recovered (R)</td>
              <td>{latestStats.R}</td>
              <td>{totalNodes > 0 ? ((latestStats.R / totalNodes) * 100).toFixed(1) : 0}%</td>
              <td>Immune</td>
            </tr>
            <tr className="sir-row dead">
              <td>Dead (D)</td>
              <td>{latestStats.D}</td>
              <td>{totalNodes > 0 ? ((latestStats.D / totalNodes) * 100).toFixed(1) : 0}%</td>
              <td>Deceased</td>
            </tr>
            <tr className="sir-row total">
              <td><strong>Total</strong></td>
              <td><strong>{totalNodes}</strong></td>
              <td><strong>100%</strong></td>
              <td>Population</td>
            </tr>
          </tbody>
        </table>
      </div>
    )
  }



  const [isSimulating, setIsSimulating] = useState(false)
  const simulationIntervalRef = useRef(null)
  const [initialInfected, setInitialInfected] = useState(3)

  const updateStatus = useCallback((msg, type = 'info') => {
    setStatus(msg)
    setStatusType(type)
  }, [])

  const handleGenerateNetwork = async () => {
    setLoading(true)
    updateStatus(`Generating ${genMethod} network...`, 'loading')
    try {
      const res = await generateNetwork({
        n_nodes: Number(nNodes),
        method: genMethod,
        avg_degree: Number(avgDegree),
        n_communities: 4,
        seed: null
      })
      updateStatus(`Network generated: ${res.nodes} nodes, ${res.edges} edges`, 'success')
      const g = await getGraph()
      setGraph(g)
      const initialStates = {}
      g.nodes.forEach(n => {
        initialStates[n.id] = n.state
      })
      setNodeStates(initialStates)
    } catch (e) {
      updateStatus('Generation failed: ' + e.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleSim = async () => {
    setLoading(true)
    setIsSimulating(true)
    setHistory([])
    updateStatus('Starting simulation...', 'loading')
    
    let isRunning = true
    let currentStep = 0
    let fullHistory = []
    
    const runAnimation = () => {
      if (!isRunning || fullHistory.length === 0) return
      
      if (currentStep < fullHistory.length) {
        const stats = fullHistory[currentStep]
        
        if (stats.nodes) {
          if (networkRef.current) {
            networkRef.current.updateNodeStates(stats.nodes)
          }
        }
        
        setHistory(fullHistory.slice(0, currentStep + 1))
        updateStatus(`Step ${currentStep + 1}/${fullHistory.length} | S: ${stats.S} | I: ${stats.I} | R: ${stats.R} | D: ${stats.D}`, 'loading')
        currentStep++
        simulationIntervalRef.current = setTimeout(runAnimation, 300)
      } else {
        isRunning = false
        setIsSimulating(false)
        setLoading(false)
        updateStatus('✓ Simulation complete - all nodes recovered or dead', 'success')
      }
    }
    
    try {
      const res = await simulate({ 
        initial_infected: Number(initialInfected),
        infection_prob: Number(infectionProb),
        death_prob: Number(deathProb)
      })
      
      fullHistory = res.history
      currentStep = 0
      
      runAnimation()
    } catch (e) {
      isRunning = false
      updateStatus('❌ Simulation failed: ' + e.message, 'error')
      setLoading(false)
      setIsSimulating(false)
    }
  }

  const handleStopSim = () => {
    setIsSimulating(false)
    setLoading(false)
    if (simulationIntervalRef.current) {
      clearTimeout(simulationIntervalRef.current)
    }
    updateStatus('⏹ Simulation stopped', 'info')
  }
  
  useEffect(() => {
    return () => {
      if (simulationIntervalRef.current) {
        clearTimeout(simulationIntervalRef.current)
      }
    }
  }, [])

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 0.1, 1.5))
  }

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 0.1, 0.5))
  }

  const handleZoomReset = () => {
    setZoom(0.8)
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          padding: 24,
          font: { size: 15, weight: 700, family: 'Segoe UI, sans-serif' },
          color: '#cbd5e0',
          boxWidth: 18,
        }
      },
      tooltip: {
        backgroundColor: 'rgba(30, 41, 59, 0.98)',
        padding: 14,
        titleFont: { size: 15, weight: 700, family: 'Segoe UI, sans-serif' },
        bodyFont: { size: 14, family: 'Segoe UI, sans-serif' },
        cornerRadius: 10,
        displayColors: true,
        borderColor: '#6366f1',
        borderWidth: 1.5,
        callbacks: {
          label: function(context) {
            return context.dataset.label + ': ' + Math.round(context.parsed.y)
          }
        }
      }
    },
    layout: {
      padding: { left: 10, right: 10, top: 10, bottom: 10 }
    },
    elements: {
      line: {
        borderWidth: 3,
        tension: 0.5,
      },
      point: {
        radius: 5,
        borderWidth: 2,
        hoverRadius: 7,
        hoverBorderWidth: 3,
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(129, 140, 248, 0.10)',
          drawBorder: false
        },
        ticks: {
          color: '#a5b4fc',
          font: { size: 13, weight: 600, family: 'Segoe UI, sans-serif' }
        }
      },
      x: {
        grid: { display: false },
        ticks: {
          color: '#a5b4fc',
          font: { size: 13, weight: 600, family: 'Segoe UI, sans-serif' }
        }
      }
    }
  }

  const chartData = {
    labels: history.map(h => h.step),
    datasets: [
      { 
        label: 'Susceptible (S)', 
        data: history.map(h => h.S), 
        borderColor: '#667eea', 
        backgroundColor: 'rgba(102, 126, 234, 0.1)',
        tension: 0.4, 
        fill: true,
        pointRadius: 5,
        pointBackgroundColor: '#667eea',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        borderWidth: 3
      },
      { 
        label: 'Infected (I)', 
        data: history.map(h => h.I), 
        borderColor: '#ff6b6b', 
        backgroundColor: 'rgba(255, 107, 107, 0.1)',
        tension: 0.4, 
        fill: true,
        pointRadius: 5,
        pointBackgroundColor: '#ff6b6b',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        borderWidth: 3
      },
      { 
        label: 'Recovered (R)', 
        data: history.map(h => h.R), 
        borderColor: '#51cf66', 
        backgroundColor: 'rgba(81, 207, 102, 0.1)',
        tension: 0.4, 
        fill: true,
        pointRadius: 5,
        pointBackgroundColor: '#51cf66',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        borderWidth: 3
      },
      {
        label: 'Dead (D)',
        data: history.map(h => h.D),
        borderColor: '#6c757d',
        backgroundColor: 'rgba(108, 117, 125, 0.1)',
        tension: 0.4,
        fill: true,
        pointRadius: 5,
        pointBackgroundColor: '#6c757d',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        borderWidth: 3
      }
    ]
  }

  return (
    <div className="app-root">
      <header className="app-header">
        <h1>COVID Network Simulator</h1>
        <p className="muted">Simulate SIR disease spread on synthetically generated social networks</p>
      </header>

      <main className="app-main">
        <aside className="controls">
          <section>
            <h3>🧬 Generate Synthetic</h3>
            <label>Network Type</label>
            <select value={genMethod} onChange={e => setGenMethod(e.target.value)}>
              <option value="watts_strogatz">Watts-Strogatz (Small-world)</option>
              <option value="barabasi">Barabási-Albert (Scale-free)</option>
              <option value="erdos">Erdős-Rényi (Random)</option>
              <option value="sbm">Stochastic Block Model</option>
            </select>
            <p className="method-description">
              {genMethod === 'watts_strogatz' && 'High clustering + short paths (realistic social networks)'}
              {genMethod === 'barabasi' && 'Power-law degree distribution'}
              {genMethod === 'erdos' && 'Random graph with uniform edges'}
              {genMethod === 'sbm' && 'Community structure with blocks'}
            </p>
            <label>Number of nodes</label>
            <input 
              type="number" 
              value={nNodes} 
              onChange={e => setNNodes(e.target.value)}
              min={10}
              max={500}
              disabled={loading}
            />
            <label>Average degree</label>
            <input 
              type="number" 
              value={avgDegree} 
              onChange={e => setAvgDegree(e.target.value)}
              min={2}
              max={50}
              disabled={loading}
            />
            <button 
              className="btn" 
              onClick={handleGenerateNetwork}
              disabled={loading}
            >
              {loading ? '⏳ Generating...' : 'Generate network'}
            </button>
          </section>

          <section>
            <h3>🧬 Simulation</h3>
            <label>Initial infected nodes</label>
            <input 
              type="number" 
              value={initialInfected} 
              onChange={e => setInitialInfected(e.target.value)} 
              min={1}
              disabled={isSimulating}
            />
            
            <label>Infection probability</label>
            <div className="slider-container">
              <input 
                type="range" 
                value={infectionProb} 
                onChange={e => setInfectionProb(e.target.value)} 
                min={0}
                max={1}
                step={0.01}
                disabled={isSimulating}
                className="slider"
              />
              <span className="slider-value">{(infectionProb * 100).toFixed(0)}%</span>
            </div>
            
            <label>Death probability</label>
            <div className="slider-container">
              <input 
                type="range" 
                value={deathProb} 
                onChange={e => setDeathProb(e.target.value)} 
                min={0}
                max={1}
                step={0.01}
                disabled={isSimulating}
                className="slider"
              />
              <span className="slider-value">{(deathProb * 100).toFixed(1)}%</span>
            </div>
            
            <div className="button-group">
              <button 
                className="btn primary" 
                onClick={handleSim}
                disabled={isSimulating || !graph}
              >
                {isSimulating ? '⏳ Running...' : '▶ Run simulation'}
              </button>
              {isSimulating && (
                <button 
                  className="btn danger" 
                  onClick={handleStopSim}
                >
                  ⏹ Stop
                </button>
              )}
            </div>
          </section>

          <section>
            <h3>📍 Real-time Status</h3>
            <div className={`status ${statusType}`}>
              <span className="status-indicator"></span>
              {status}
            </div>
          </section>
        </aside>

        <section className="workspace">
          <div className="network-area">
            <h3>🕸️ Network Graph</h3>
            <div className="zoom-controls">
              <button className="zoom-btn" onClick={handleZoomOut} title="Zoom Out">−</button>
              <div className="zoom-level">{(zoom * 100).toFixed(0)}%</div>
              <button className="zoom-btn" onClick={handleZoomIn} title="Zoom In">+</button>
              <button className="zoom-btn" onClick={handleZoomReset} title="Reset Zoom">⟳</button>
            </div>
            {graph ? (
              <Network3D ref={networkRef} data={graph} zoom={zoom} onStatusUpdate={updateStatus} nodeStates={nodeStates} />
            ) : (
              <div style={{textAlign: 'center', padding: '40px', color: '#a0aec0'}}>
                Generate a network to visualize
              </div>
            )}
          </div>

          <div className="sir-container">
            <div className="sir-stats">
              <h3>📊 SIR Statistics</h3>
              <SIRStatsTable history={history} />
            </div>
            
            <div className="charts">
              <h3>📈 SIR Dynamics Over Time</h3>
              {history.length > 0 ? (
                <Line data={chartData} options={chartOptions} />
              ) : (
                <div style={{textAlign: 'center', padding: '40px', color: '#a0aec0'}}>
                  Run a simulation to see the SIR curve
                </div>
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
