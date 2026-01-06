# Edge List Network Format Guide

## Overview
The **Edge List (Direct)** method is the fastest and most straightforward way to load a pre-computed network into the COVID simulator. Use this when you already have your network edges defined.

---

## CSV Format

### Required Columns
```csv
FromNodeId,ToNodeId
```

### Data Types
- **FromNodeId**: Can be numeric (30, 1412) or string ("alice", "node_001")
- **ToNodeId**: Can be numeric (30, 1412) or string ("alice", "node_001")
- Both must be the same type across the file

### Example Data
```csv
FromNodeId,ToNodeId
30,1412
30,3352
30,5254
30,5543
30,7478
3,28
3,30
3,39
3,54
3,108
1412,5254
1412,5543
3352,5254
5254,7478
28,30
28,39
30,39
39,54
54,108
5543,7478
1412,3352
3,1412
108,30
5254,5543
39,108
```

---

## How It Works

### Network Construction
1. **Read** each row of the CSV
2. **Extract** FromNodeId and ToNodeId
3. **Create** an undirected edge between the two nodes
4. **Remove** any isolated nodes (nodes with no connections)
5. **Compute** spring layout for visualization

### Time Complexity
- **Graph Building**: O(E) where E = number of edges
- **Layout Calculation**: O(N²) where N = number of nodes
- **Total**: O(E + N²)

### Space Complexity
- **Graph Storage**: O(N + E)

---

## Creating Edge List Data

### From Adjacency Matrix
If you have a network represented as a matrix:

```python
import pandas as pd
import networkx as nx

# Load adjacency matrix
adj_matrix = pd.read_csv('adjacency_matrix.csv', index_col=0)

# Convert to edge list
edge_list = []
for i in range(len(adj_matrix)):
    for j in range(i+1, len(adj_matrix)):
        if adj_matrix.iloc[i, j] > 0:  # If there's a connection
            edge_list.append({
                'FromNodeId': adj_matrix.index[i],
                'ToNodeId': adj_matrix.columns[j]
            })

# Save as CSV
df = pd.DataFrame(edge_list)
df.to_csv('network_edgelist.csv', index=False)
```

### From NetworkX Graph
```python
import networkx as nx
import pandas as pd

# Load or create graph
G = nx.read_graphml('network.graphml')  # or any other format

# Convert to edge list CSV
edges = list(G.edges())
df = pd.DataFrame(edges, columns=['FromNodeId', 'ToNodeId'])
df.to_csv('network_edgelist.csv', index=False)
```

### From Social Network Platforms
**Twitter Network Example:**
```python
# Connect users who mention each other
edge_list = []
for user_a in users:
    mentions = get_mentions(user_a)  # Get users mentioned by user_a
    for user_b in mentions:
        edge_list.append({
            'FromNodeId': user_a['id'],
            'ToNodeId': user_b['id']
        })

df = pd.DataFrame(edge_list).drop_duplicates()
df.to_csv('twitter_network.csv', index=False)
```

### From Collaboration Networks
```python
# Connect authors who collaborated on papers
edge_list = []
for paper in papers:
    authors = paper['authors']
    for i in range(len(authors)):
        for j in range(i+1, len(authors)):
            edge_list.append({
                'FromNodeId': authors[i],
                'ToNodeId': authors[j]
            })

df = pd.DataFrame(edge_list).drop_duplicates()
df.to_csv('collaboration_network.csv', index=False)
```

---

## Best Practices

### ✅ Do's

1. **Keep IDs consistent**
   ```csv
   FromNodeId,ToNodeId
   1,2
   1,3
   2,3
   ```
   
2. **Remove duplicates** (optional, but cleaner)
   ```python
   df = df.drop_duplicates()
   ```

3. **Use meaningful IDs** when possible
   ```csv
   FromNodeId,ToNodeId
   alice,bob
   alice,carol
   bob,carol
   ```

4. **Avoid self-loops** (node connecting to itself)
   ```python
   df = df[df['FromNodeId'] != df['ToNodeId']]
   ```

5. **Check for whitespace**
   ```python
   df['FromNodeId'] = df['FromNodeId'].astype(str).str.strip()
   df['ToNodeId'] = df['ToNodeId'].astype(str).str.strip()
   ```

### ❌ Don'ts

1. **Don't include header row twice**
   ```
   ❌ WRONG:
   FromNodeId,ToNodeId,FromNodeId,ToNodeId
   1,2,1,2
   
   ✅ RIGHT:
   FromNodeId,ToNodeId
   1,2
   ```

2. **Don't mix node ID types**
   ```
   ❌ WRONG:
   FromNodeId,ToNodeId
   1,alice
   2,bob
   
   ✅ RIGHT (all numeric):
   FromNodeId,ToNodeId
   1,2
   2,3
   
   ✅ RIGHT (all string):
   FromNodeId,ToNodeId
   alice,bob
   bob,carol
   ```

3. **Don't include extra columns** (they'll be ignored)
   ```
   ❌ PROBLEMATIC:
   FromNodeId,ToNodeId,Weight,Type
   1,2,0.5,friend
   1,3,0.8,colleague
   
   ✅ BETTER:
   FromNodeId,ToNodeId
   1,2
   1,3
   ```

4. **Don't forget to strip whitespace**
   ```
   ❌ WRONG (extra spaces):
   FromNodeId,ToNodeId
   " 1 "," 2 "
   
   ✅ RIGHT:
   FromNodeId,ToNodeId
   1,2
   ```

---

## Performance Considerations

### File Size Impact
| Nodes | Edges | Build Time | Memory |
|-------|-------|-----------|--------|
| 100 | 500 | <0.1s | ~1MB |
| 1,000 | 5,000 | ~0.2s | ~5MB |
| 10,000 | 50,000 | ~0.5s | ~50MB |
| 100,000 | 500,000 | ~2s | ~500MB |

### Layout Computation
- Spring layout is slower for large graphs
- Recommendation: Keep networks under 5,000 nodes for smooth visualization
- For larger networks: Pre-compute layout in NetworkX, export positions separately

---

## Troubleshooting

### Problem: "No graph built" or Empty Network

**Symptom**: CSV uploads successfully but network shows no nodes

**Causes**:
1. Wrong column names (not "FromNodeId" and "ToNodeId")
2. No valid edges in file
3. All nodes are isolated (get removed automatically)

**Solution**:
```python
# Check your CSV
df = pd.read_csv('your_file.csv')
print(df.columns)  # Must have 'FromNodeId' and 'ToNodeId'
print(df.head())   # Check data looks correct
print(len(df))     # Should have rows
```

### Problem: Node IDs Not Recognized

**Symptom**: Graph builds but node IDs are unexpected values

**Cause**: Whitespace in IDs

**Solution**:
```python
df['FromNodeId'] = df['FromNodeId'].astype(str).str.strip()
df['ToNodeId'] = df['ToNodeId'].astype(str).str.strip()
df.to_csv('cleaned.csv', index=False)
```

### Problem: Very Few Edges in Visualization

**Symptom**: Uploaded 1000 edges but graph shows only 10-20

**Cause**: Isolated nodes automatically removed; most nodes have no edges

**Solution**: Check edge distribution
```python
from collections import Counter

df = pd.read_csv('your_file.csv')
all_nodes = list(df['FromNodeId']) + list(df['ToNodeId'])
degree = Counter(all_nodes)
print(degree.most_common(10))  # Top 10 connected nodes
```

---

## Examples

### Example 1: Small Contact Network
```csv
FromNodeId,ToNodeId
alice,bob
alice,carol
bob,carol
carol,dave
dave,eve
```
**Network**: 5 nodes, 5 edges
**Use case**: Small social group disease spread

### Example 2: Collaboration Network
```csv
FromNodeId,ToNodeId
author_1,author_2
author_1,author_3
author_2,author_4
author_3,author_5
author_4,author_5
```
**Network**: 5 nodes, 5 edges
**Use case**: Information spread among researchers

### Example 3: Large Social Network
```csv
FromNodeId,ToNodeId
1,2
1,3
1,4
2,3
2,5
...
9999,10000
```
**Network**: 10,000 nodes, 50,000 edges
**Use case**: Large-scale epidemic simulation

---

## Converting Other Formats

### From GML (Graph Markup Language)
```python
import networkx as nx
import pandas as pd

G = nx.read_gml('network.gml')
edges = [(str(u), str(v)) for u, v in G.edges()]
df = pd.DataFrame(edges, columns=['FromNodeId', 'ToNodeId'])
df.to_csv('network_edgelist.csv', index=False)
```

### From GexF (Graph Exchange XML)
```python
import networkx as nx
import pandas as pd

G = nx.read_gexf('network.gexf')
edges = [(str(u), str(v)) for u, v in G.edges()]
df = pd.DataFrame(edges, columns=['FromNodeId', 'ToNodeId'])
df.to_csv('network_edgelist.csv', index=False)
```

### From Pajek Format
```python
import networkx as nx
import pandas as pd

G = nx.read_pajek('network.net')
edges = [(str(u), str(v)) for u, v in G.edges()]
df = pd.DataFrame(edges, columns=['FromNodeId', 'ToNodeId'])
df.to_csv('network_edgelist.csv', index=False)
```

---

## Integration with Simulation

### Workflow
1. **Create** your edge list CSV file
2. **Upload** via "Drop CSV here" button
3. **Select** "Edge List (Direct)" from dropdown
4. **Click** "Build network" button
5. **Wait** for graph visualization
6. **Configure** simulation parameters
7. **Run** simulation to observe disease spread

### Quick Commands
```bash
# Validate edge list format
python -c "
import pandas as pd
df = pd.read_csv('network.csv')
assert set(df.columns) == {'FromNodeId', 'ToNodeId'}
assert len(df) > 0
print(f'Valid! {len(df)} edges, {len(set(list(df.FromNodeId) + list(df.ToNodeId)))} nodes')
"

# Clean and save
python -c "
import pandas as pd
df = pd.read_csv('network.csv')
df['FromNodeId'] = df['FromNodeId'].astype(str).str.strip()
df['ToNodeId'] = df['ToNodeId'].astype(str).str.strip()
df = df[df['FromNodeId'] != df['ToNodeId']].drop_duplicates()
df.to_csv('network_cleaned.csv', index=False)
print(f'Saved {len(df)} edges')
"
```

---

**Ready to load your network? Create your edge list CSV and upload it!** 🚀
