# Backend (FastAPI)

This folder contains a FastAPI backend exposing endpoints for the COVID network simulator.

Quickstart (recommended inside a virtualenv):

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API endpoints:
- `POST /upload-csv` : upload a CSV dataset (form file field `file`)
- `POST /build-network?method=copresence|hashtag|text` : build graph from uploaded dataset
- `GET /graph` : returns JSON with nodes/edges and node positions
- `POST /simulate` : run SIR simulation (query params: `infection_prob`, `recovery_prob`, `steps`, `initial_infected`)
- `GET /download/graph` : download NetworkX gpickle
