# generated: 2025-12-04
# System Auto: last updated on: 2025-12-04 23:26:34
# NetworkX - Python Graph Library
## Library Reference for HAIOS

> **Source:** Context7 `/networkx/networkx` (Benchmark: 80.3)
> **Extracted:** 2025-12-04
> **Related Report:** @docs/reports/2025-12-04-REPORT-multi-index-architecture.md

---

## Overview

NetworkX is a Python library for the creation, manipulation, and study of complex networks. It provides data structures for graphs (directed, undirected, multigraphs) and algorithms for graph analysis.

### Relevance to HAIOS
Per the Multi-Index Architecture report, NetworkX enables:
- Graph index for relational and multi-hop reasoning
- Entity relationship traversal
- Export to JSON-LD for complex analysis

---

## Installation

```bash
pip install networkx
```

---

## Core API

### Create Graphs

```python
import networkx as nx

# Basic graph types
G = nx.Graph()          # Undirected
D = nx.DiGraph()        # Directed
M = nx.MultiGraph()     # Undirected with parallel edges
MD = nx.MultiDiGraph()  # Directed with parallel edges
```

### Add Nodes

```python
# Single node
G.add_node(1)

# Multiple nodes
G.add_nodes_from([2, 3, 4, 5])
G.add_nodes_from(range(6, 10))

# Node with attributes
G.nodes[1]["label"] = "Start"
G.nodes[1]["type"] = "entity"
```

### Add Edges

```python
# Single edge
G.add_edge(1, 2)

# Multiple edges
G.add_edges_from([(1, 3), (2, 4), (3, 4)])

# Edge with attributes (for weighted graphs)
G.add_edge(5, 6, weight=4.5, relation="MENTIONS")
G.add_edges_from([(6, 7), (7, 8)], relation="DERIVED_FROM")
```

### Query Graph

```python
# Counts
print(f"Nodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")

# Node degree
print(f"Degree of node 4: {G.degree(4)}")

# Neighbors
print(f"Neighbors of node 1: {list(G.neighbors(1))}")

# Membership
print(1 in G)              # True
print(G.has_edge(1, 2))    # True

# Access attributes
print(G.edges[5, 6]["weight"])
```

### Remove Elements

```python
# Remove node (also removes incident edges)
G.remove_node(2)
G.remove_nodes_from([3, 4])

# Remove edge
G.remove_edge(1, 3)
```

---

## Graph Construction Patterns

### From Edge List

```python
edgelist = [(0, 1), (1, 2), (2, 3)]
H = nx.Graph(edgelist)
```

### From Adjacency Dict

```python
adjacency_dict = {0: (1, 2), 1: (0, 2), 2: (0, 1)}
H = nx.Graph(adjacency_dict)
```

### From Existing Graph

```python
# Create DiGraph from undirected Graph
H = nx.DiGraph(G)
```

---

## Traversal Algorithms

### Shortest Path (Dijkstra)

```python
# Create weighted graph
G = nx.DiGraph()
edges = [
    ("S", "A", 3), ("S", "B", 5),
    ("A", "C", 2), ("B", "C", 1),
    ("C", "D", 4)
]
for u, v, w in edges:
    G.add_edge(u, v, weight=w)

# Single source to target
path_length, path = nx.single_source_dijkstra(G, source="S", target="D", weight="weight")
print(f"Path: {path}, Length: {path_length}")

# All paths from source
lengths, paths = nx.single_source_dijkstra(G, source="S", weight="weight")
```

### Connected Components

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3)])
G.add_node("isolated")

components = list(nx.connected_components(G))
# [{1, 2, 3}, {'isolated'}]
```

### Ancestors/Descendants (for DiGraph)

```python
D = nx.DiGraph()
D.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 4)])

ancestors = nx.ancestors(D, 4)    # {1, 2, 3}
descendants = nx.descendants(D, 1)  # {2, 3, 4}
```

---

## HAIOS Integration Pattern

### Graph Index Schema (from Multi-Index Report)

```python
import networkx as nx

# Create HAIOS knowledge graph
kg = nx.DiGraph()

# Add entity nodes
kg.add_node("entity_1", type="Entity", value="DatabaseManager")
kg.add_node("artifact_1", type="Artifact", file_path="database.py")
kg.add_node("concept_1", type="Concept", content="Idempotency")

# Add relationship edges
kg.add_edge("entity_1", "artifact_1", relation="EXTRACTED_FROM")
kg.add_edge("artifact_1", "concept_1", relation="IMPLEMENTS")
kg.add_edge("concept_1", "concept_2", relation="DERIVED_FROM")

# Query: Find all concepts related to an entity
def find_related_concepts(graph, entity_id):
    related = set()
    for neighbor in nx.descendants(graph, entity_id):
        if graph.nodes[neighbor].get("type") == "Concept":
            related.add(neighbor)
    return related
```

### Export to JSON for Storage

```python
import json
from networkx.readwrite import json_graph

# Export graph to JSON
data = json_graph.node_link_data(kg)
json_str = json.dumps(data)

# Import graph from JSON
loaded_data = json.loads(json_str)
kg_restored = json_graph.node_link_graph(loaded_data)
```

---

## Performance Notes

- NetworkX is pure Python - good for small-medium graphs
- For large graphs (>100k nodes), consider:
  - `graph-tool` (C++ backend)
  - `igraph` (C backend)
  - `rustworkx` (Rust backend, benchmark 87.1)

---

## References

- GitHub: https://github.com/networkx/networkx
- Docs: https://networkx.org/documentation/stable/
- PyPI: https://pypi.org/project/networkx/

---

**END OF LIBRARY REFERENCE**
