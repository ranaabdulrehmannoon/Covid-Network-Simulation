from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import pandas as pd
import io
import os
import tempfile
from typing import Dict, Any

from . import simulator

app = FastAPI(title="COVID Network Simulator API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# in-memory store (simple)
store: Dict[str, Any] = {"df": None, "G": None, "pos": None}


@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")
    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
        df.columns = [c.strip() for c in df.columns]
        # parse timestamps if present
        if "Timestamp" in df.columns:
            try:
                df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
            except Exception:
                pass
        store["df"] = df
        return {"rows": len(df), "columns": list(df.columns)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/build-network")
def build_network(method: str = "copresence"):
    df = store.get("df")
    if df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded. Call /upload-csv first.")
    try:
        G, pos = simulator.build_network_from_df(df, method=method)
        store["G"] = G
        store["pos"] = pos
        stats = {"nodes": G.number_of_nodes(), "edges": G.number_of_edges()}
        # compute top-degree sample
        degs = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:10]
        stats["top_degree"] = [{"node": n, "deg": int(d)} for n, d in degs]
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-network")
def generate_network(n_nodes: int = 2000, method: str = "barabasi", avg_degree: float = 6.0, n_communities: int = 4, seed: int = None):
    """Generate a synthetic network server-side. Returns basic stats."""
    try:
        G, pos = simulator.generate_synthetic_graph(n_nodes=n_nodes, method=method, avg_degree=avg_degree, n_communities=n_communities, seed=seed)
        store["G"] = G
        store["pos"] = pos
        stats = {"nodes": G.number_of_nodes(), "edges": G.number_of_edges(), "method": method}
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/graph")
def get_graph():
    G = store.get("G")
    pos = store.get("pos")
    if G is None:
        return {"nodes": [], "edges": []}
    if G.number_of_nodes() > 100:
        raise HTTPException(status_code=400, detail=f"Network too large: {G.number_of_nodes()} nodes (max 100)")
    data = simulator.graph_to_json(G, pos)
    return data


@app.post("/simulate")
def run_simulation(initial_infected: int = 3, infection_prob: float = 0.5, death_prob: float = 0.12):
    G = store.get("G")
    if G is None:
        raise HTTPException(status_code=400, detail="No graph built. Call /build-network first.")
    if infection_prob < 0 or infection_prob > 1:
        raise HTTPException(status_code=400, detail="infection_prob must be between 0 and 1")
    if death_prob < 0 or death_prob > 1:
        raise HTTPException(status_code=400, detail="death_prob must be between 0 and 1")
    infected = simulator.reset_states(G, initial_infected=initial_infected, infection_prob=infection_prob)
    history = simulator.simulate_sir_realtime(G, death_prob=death_prob)
    store["G"] = G
    return {"initial_infected": len(infected), "history": history}


@app.get("/download/graph")
def download_graph():
    G = store.get("G")
    if G is None:
        raise HTTPException(status_code=400, detail="No graph available")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".gpickle")
    path = tmp.name
    tmp.close()
    import networkx as nx
    nx.write_gpickle(G, path)
    return FileResponse(path, filename="graph.gpickle", media_type="application/octet-stream")


@app.get("/download/edgelist")
def download_edgelist():
    G = store.get("G")
    if G is None:
        raise HTTPException(status_code=400, detail="No graph available")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode='w')
    path = tmp.name
    tmp.write("FromNodeId,ToNodeId\n")
    for u, v in G.edges():
        tmp.write(f"{u},{v}\n")
    tmp.close()
    return FileResponse(path, filename="network_edgelist.csv", media_type="text/csv")
