"""
Lightweight simulator core extracted from the Tkinter app.
Provides functions to build networks and run SIR simulations programmatically.
"""
from typing import Dict, Any, List, Tuple, Optional
import math
import time
import numpy as np
import pandas as pd
import networkx as nx

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False


def build_network_from_df(df: pd.DataFrame, method: str = "copresence") -> Tuple[nx.Graph, Dict[str, Tuple[float,float]]]:
    """Builds and returns a NetworkX graph and a spring layout position dict.
    
    Supported methods:
    - 'copresence': Groups users by location/time co-occurrence. Requires 'User' column.
    - 'hashtag': Connects users sharing hashtags. Requires 'User' and 'Hashtags' columns.
    - 'text': Connects users with similar text content. Requires 'User' and 'Text' columns.
    - 'edgelist': Direct edge list. Requires 'FromNodeId' and 'ToNodeId' columns.
    """
    G = nx.Graph()
    if df is None or len(df) == 0:
        return G, {}
    df = df.copy()
    
    if method == "edgelist":
        if "FromNodeId" not in df.columns or "ToNodeId" not in df.columns:
            raise ValueError("Dataset must contain 'FromNodeId' and 'ToNodeId' columns for edgelist method")
        df["FromNodeId"] = df["FromNodeId"].astype(str).str.strip()
        df["ToNodeId"] = df["ToNodeId"].astype(str).str.strip()
        for _, row in df.iterrows():
            from_node = row["FromNodeId"]
            to_node = row["ToNodeId"]
            if from_node and to_node and from_node != to_node:
                G.add_edge(from_node, to_node)
    elif "User" not in df.columns:
        raise ValueError("Dataset must contain 'User' column for copresence, hashtag, or text methods")
    else:
        df["User"] = df["User"].astype(str).str.strip()

    if method != "edgelist":
        if method == "copresence":
            if "Timestamp" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["Timestamp"]):
                try:
                    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
                except Exception:
                    pass
            if "Timestamp" in df.columns and pd.api.types.is_datetime64_any_dtype(df["Timestamp"]):
                df["Year"] = df["Timestamp"].dt.year
                df["Month"] = df["Timestamp"].dt.month
                df["Day"] = df["Timestamp"].dt.day
                df["Hour"] = df["Timestamp"].dt.hour
            grouped = df.groupby([c for c in ["Country","Year","Month","Day","Hour"] if c in df.columns])
            for _, group in grouped:
                users = group["User"].unique()
                for u, v in combinations(users, 2):
                    if u != v:
                        G.add_edge(u, v)

        elif method == "hashtag":
            df["Hashtags"] = df.get("Hashtags", "").astype(str)
            bip = nx.Graph()
            for _, row in df.iterrows():
                user = row["User"]
                tags_raw = row["Hashtags"]
                if pd.isna(tags_raw) or tags_raw == "nan":
                    tags = []
                else:
                    tokens = [tok.strip().strip(",") for tok in tags_raw.split() if tok.strip()]
                    tags = []
                    for tok in tokens:
                        if tok.startswith("#"):
                            tags.append(tok.lower())
                        else:
                            for t in tok.split(","):
                                t = t.strip()
                                if t.startswith("#"):
                                    tags.append(t.lower())
                for tag in tags:
                    bip.add_node(user, bipartite=0)
                    bip.add_node(tag, bipartite=1)
                    bip.add_edge(user, tag)
            users = [n for n, d in bip.nodes(data=True) if d.get("bipartite") == 0]
            if users:
                G = nx.bipartite.projected_graph(bip, users)

        elif method == "text":
            if not SKLEARN_AVAILABLE:
                raise RuntimeError("scikit-learn not available for text similarity method")
            if "Text" not in df.columns:
                raise ValueError("Dataset must contain 'Text' column for text-similarity method")
            texts = df["Text"].fillna("").astype(str).tolist()
            users = df["User"].astype(str).tolist()
            vec = TfidfVectorizer(stop_words="english", max_features=2000)
            X = vec.fit_transform(texts)
            sim = cosine_similarity(X)
            threshold = 0.45
            for i in range(len(users)):
                for j in range(i+1, len(users)):
                    if sim[i, j] > threshold:
                        G.add_edge(users[i], users[j])
        else:
            raise ValueError(f"Unknown method {method}")

    # remove isolates
    if G.number_of_nodes() > 0:
        isolates = list(nx.isolates(G))
        G.remove_nodes_from(isolates)
    # layout
    pos = {}
    if G.number_of_nodes() > 0:
        try:
            k = 1.0 / math.sqrt(max(1, G.number_of_nodes()))
            pos = nx.spring_layout(G, k=k, iterations=80)
        except Exception:
            pos = nx.spring_layout(G)
    return G, pos


def generate_synthetic_graph(n_nodes: int = 2000, method: str = "barabasi", avg_degree: float = 6, n_communities: int = 4, seed: Optional[int] = None) -> Tuple[nx.Graph, Dict[str, Tuple[float, float]]]:
    """Generate a synthetic social network.

    Methods supported:
    - "barabasi": Barabási–Albert preferential attachment (scale-free)
    - "erdos": Erdős–Rényi random graph (G(n, p) with p chosen from avg_degree)
    - "sbm": Stochastic Block Model with `n_communities` blocks
    - "watts_strogatz": Watts–Strogatz small-world network (high clustering + short path lengths)

    Returns (G, pos) where pos is a spring_layout dict.
    """
    if seed is None:
        seed = int(time.time()) % 100000
    rng = np.random.RandomState(seed=seed)
    G = nx.Graph()
    if n_nodes <= 0:
        return G, {}

    if method == "barabasi":
        # choose m (edges to attach) from avg_degree/2 approximated
        m = max(1, int(max(1, round(avg_degree / 2))))
        G = nx.barabasi_albert_graph(n_nodes, m, seed=seed)

    elif method == "erdos":
        # p = avg_degree / (n-1)
        p = float(avg_degree) / max(1, (n_nodes - 1))
        G = nx.erdos_renyi_graph(n_nodes, p, seed=seed)

    elif method == "sbm" or method == "stochastic":
        # create balanced community sizes
        sizes = [n_nodes // n_communities] * n_communities
        for i in range(n_nodes % n_communities):
            sizes[i] += 1
        # intra-community probability higher than inter
        pin = min(0.2, float(avg_degree) / max(1, (sizes[0]-1)))
        pout = max(0.001, pin * 0.05)
        probs = [[pin if i == j else pout for j in range(n_communities)] for i in range(n_communities)]
        G = nx.stochastic_block_model(sizes, probs, seed=seed)

    elif method == "watts_strogatz":
        # Watts-Strogatz small-world network
        k = int(max(2, avg_degree))
        if k % 2 == 1:
            k += 1
        p = 0.1
        G = nx.watts_strogatz_graph(n_nodes, k, p, seed=seed)

    else:
        raise ValueError(f"Unknown synthetic method: {method}")

    # remove isolates for cleaner visualization
    if G.number_of_nodes() > 0:
        isolates = list(nx.isolates(G))
        G.remove_nodes_from(isolates)

    pos = {}
    if G.number_of_nodes() > 0:
        try:
            k = 1.0 / math.sqrt(max(1, G.number_of_nodes()))
            pos = nx.spring_layout(G, k=k, iterations=80, seed=seed)
        except Exception:
            pos = nx.spring_layout(G)

    return G, pos


# Helper needed for combinations
from itertools import combinations


def reset_states(G: nx.Graph, initial_infected: int = 3, infection_prob: float = 0.5, seed: int = None) -> List[str]:
    if G is None:
        return []
    nodes = list(G.nodes())
    if seed is None:
        seed = int(time.time()) % 100000
    rng = np.random.RandomState(seed=seed)
    infection_prob = max(0.01, min(1.0, infection_prob))
    for n in nodes:
        G.nodes[n]["state"] = "S"
        G.nodes[n]["infection_prob"] = float(infection_prob)
        G.nodes[n]["recovery_prob"] = float(rng.uniform(0.3, 0.9))
        G.nodes[n]["dead"] = False
    k = max(1, int(initial_infected))
    if k >= len(nodes):
        k = max(1, len(nodes) // 10)
    infected = rng.choice(nodes, size=min(k, len(nodes)), replace=False).tolist() if nodes else []
    for u in infected:
        G.nodes[u]["state"] = "I"
    return infected


def simulate_sir_realtime(G: nx.Graph, death_prob: float = 0.12) -> List[Dict[str, Any]]:
    """
    Simulate SIR with node-level infection/recovery probabilities and death state.
    Returns history with node states at each step.
    """
    history = []
    if G is None or G.number_of_nodes() == 0:
        return history
    death_prob = max(0, min(1, death_prob))
    def record(s):
        node_states = {}
        S = I = R = D = 0
        for n in G.nodes():
            state = G.nodes[n].get("state", "S")
            node_states[str(n)] = state
            if state == "S": S += 1
            elif state == "I": I += 1
            elif state == "R": R += 1
            elif state == "D": D += 1
        history.append({"step": s, "S": S, "I": I, "R": R, "D": D, "nodes": node_states})
    record(0)
    step = 0
    while True:
        to_infect = set()
        to_recover = set()
        to_die = set()
        for node in list(G.nodes()):
            state = G.nodes[node].get("state")
            if state == "I":
                if np.random.rand() < death_prob:
                    to_die.add(node)
                    continue
                for nbr in G.neighbors(node):
                    if G.nodes[nbr].get("state") == "S":
                        if np.random.rand() < G.nodes[node].get("infection_prob", 0.5):
                            to_infect.add(nbr)
                if np.random.rand() < G.nodes[node].get("recovery_prob", 0.5):
                    to_recover.add(node)
        for n in to_infect:
            G.nodes[n]["state"] = "I"
        for r in to_recover:
            G.nodes[r]["state"] = "R"
        for d in to_die:
            G.nodes[d]["state"] = "D"
            G.nodes[d]["dead"] = True
        step += 1
        record(step)
        S = sum(1 for n in G.nodes() if G.nodes[n].get("state") == "S")
        I = sum(1 for n in G.nodes() if G.nodes[n].get("state") == "I")
        if S == 0 and I == 0:
            break
        if step > 10000:
            break
    return history


def graph_to_json(G: nx.Graph, pos: Dict[str, Tuple[float, float]] = None) -> Dict[str, Any]:
    nodes = []
    for n in G.nodes():
        x, y = (0.0, 0.0)
        if pos and n in pos:
            x, y = float(pos[n][0]), float(pos[n][1])
        nodes.append({
            "id": str(n),
            "state": G.nodes[n].get("state", "S"),
            "x": x,
            "y": y,
            "infection_prob": G.nodes[n].get("infection_prob", None),
            "recovery_prob": G.nodes[n].get("recovery_prob", None),
            "dead": G.nodes[n].get("dead", False)
        })
    edges = []
    for u, v in G.edges():
        edges.append({"u": str(u), "v": str(v)})
    return {"nodes": nodes, "edges": edges}
