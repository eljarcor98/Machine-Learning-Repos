from __future__ import annotations

import networkx as nx
import pandas as pd

from src.data.load_cicids2017 import resolve_network_columns


def build_flow_graph(
    df: pd.DataFrame,
    source_column: str | None = None,
    destination_column: str | None = None,
    label_column: str = "label_normalized",
) -> nx.DiGraph:
    if df.empty:
        raise ValueError("El DataFrame esta vacio; no se puede construir un grafo.")

    resolved_source, resolved_destination = resolve_network_columns(df)
    source_column = source_column or resolved_source
    destination_column = destination_column or resolved_destination

    graph = nx.DiGraph()

    for row in df.itertuples(index=False):
        source = getattr(row, source_column.replace(" ", "_"))
        destination = getattr(row, destination_column.replace(" ", "_"))
        label = getattr(row, label_column, "unknown")

        if pd.isna(source) or pd.isna(destination):
            continue

        if graph.has_edge(source, destination):
            graph[source][destination]["weight"] += 1
            graph[source][destination]["labels"].add(label)
        else:
            graph.add_edge(source, destination, weight=1, labels={label})

    return graph


def top_nodes_by_degree(graph: nx.DiGraph, n: int = 10) -> list[tuple[str, int]]:
    degree_view = graph.degree()
    return sorted(degree_view, key=lambda item: item[1], reverse=True)[:n]


def graph_summary(graph: nx.DiGraph) -> dict[str, float]:
    if graph.number_of_nodes() == 0:
        return {
            "nodes": 0,
            "edges": 0,
            "density": 0.0,
        }

    return {
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "density": float(nx.density(graph)),
    }
