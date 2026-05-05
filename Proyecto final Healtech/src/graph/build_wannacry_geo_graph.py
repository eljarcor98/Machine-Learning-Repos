from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


DEFAULT_HOSTS = Path("data/processed/hybrid_analysis_contacted_hosts_geo.csv")
DEFAULT_COUNTRIES = Path("data/processed/hybrid_analysis_contacted_countries.csv")
DEFAULT_HOST_GRAPHML = Path("data/processed/wannacry_realistic_geo_host_graph.graphml")
DEFAULT_COUNTRY_GRAPHML = Path("data/processed/wannacry_realistic_geo_country_graph.graphml")
DEFAULT_METADATA = Path("data/processed/wannacry_realistic_geo_graph_metadata.json")
DEFAULT_FIGURE = Path("reports/figures/wannacry_realistic_geo_graph.png")
SOURCE_NODE = "Sandbox_WannaCry_mssecsvc.exe"


def load_inputs(hosts_path: Path, countries_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not hosts_path.exists():
        raise FileNotFoundError(f"No existe {hosts_path}. Ejecuta parse_hybrid_analysis_hosts.py primero.")
    if not countries_path.exists():
        raise FileNotFoundError(f"No existe {countries_path}. Ejecuta parse_hybrid_analysis_hosts.py primero.")

    hosts = pd.read_csv(hosts_path)
    countries = pd.read_csv(countries_path)
    for df in (hosts, countries):
        df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
        df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    return hosts, countries


def deterministic_jitter(ip: str, hosts_in_country: int) -> tuple[float, float]:
    seed = sum(ord(char) for char in ip)
    rng = random.Random(seed)
    radius = min(4.5, 0.7 + math.log1p(max(hosts_in_country, 1)) * 0.65)
    angle = rng.uniform(0, math.tau)
    distance = rng.uniform(0.1, radius)
    return math.sin(angle) * distance, math.cos(angle) * distance


def build_host_graph(hosts: pd.DataFrame) -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_node(
        SOURCE_NODE,
        node_type="malware_process",
        label="mssecsvc.exe",
        process="mssecsvc.exe",
        pid="3192",
        latitude=0.0,
        longitude=0.0,
        country="Sandbox",
    )

    country_counts = hosts["country"].value_counts().to_dict()
    for row in hosts.itertuples(index=False):
        if pd.isna(row.latitude) or pd.isna(row.longitude):
            continue

        offset_lat, offset_lon = deterministic_jitter(str(row.ip), int(country_counts.get(row.country, 1)))
        host_lat = float(row.latitude) + offset_lat
        host_lon = float(row.longitude) + offset_lon
        graph.add_node(
            row.ip,
            node_type="contacted_host",
            label=row.ip,
            country=row.country,
            latitude=round(host_lat, 6),
            longitude=round(host_lon, 6),
            country_centroid_latitude=float(row.latitude),
            country_centroid_longitude=float(row.longitude),
            asn="" if pd.isna(row.asn) else str(row.asn),
            organization="" if pd.isna(row.organization) else str(row.organization),
        )
        graph.add_edge(
            SOURCE_NODE,
            row.ip,
            protocol=row.protocol,
            port=str(row.port),
            process=row.process,
            pid=str(row.pid),
            relationship="contacted_host",
            weight=1,
        )
    return graph


def build_country_graph(countries: pd.DataFrame) -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_node(
        SOURCE_NODE,
        node_type="malware_process",
        label="mssecsvc.exe",
        latitude=0.0,
        longitude=0.0,
        country="Sandbox",
    )

    for row in countries.itertuples(index=False):
        if pd.isna(row.latitude) or pd.isna(row.longitude):
            continue
        country_id = f"Country::{row.country}"
        graph.add_node(
            country_id,
            node_type="country",
            label=row.country,
            country=row.country,
            latitude=float(row.latitude),
            longitude=float(row.longitude),
            hosts=int(row.hosts),
        )
        graph.add_edge(
            SOURCE_NODE,
            country_id,
            relationship="country_contact_count",
            weight=int(row.hosts),
            hosts=int(row.hosts),
        )
    return graph


def plot_geo_graph(hosts: pd.DataFrame, countries: pd.DataFrame, output_path: Path) -> None:
    hosts_geo = hosts.dropna(subset=["latitude", "longitude"]).copy()
    countries_geo = countries.dropna(subset=["latitude", "longitude"]).copy()
    country_counts = hosts_geo["country"].value_counts().to_dict()

    jittered_points = []
    for row in hosts_geo.itertuples(index=False):
        offset_lat, offset_lon = deterministic_jitter(str(row.ip), int(country_counts.get(row.country, 1)))
        jittered_points.append(
            {
                "ip": row.ip,
                "country": row.country,
                "latitude": float(row.latitude) + offset_lat,
                "longitude": float(row.longitude) + offset_lon,
                "port": row.port,
                "asn": row.asn,
            }
        )
    host_points = pd.DataFrame(jittered_points)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(15, 8))
    ax.set_facecolor("#f6f8fa")
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 85)
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.set_title("WannaCry - grafo geografico realista de hosts contactados", fontweight="bold")
    ax.grid(alpha=0.22)

    # Approximate sandbox origin as a neutral logical source, not a real location.
    source_lon, source_lat = 0.0, 0.0
    top_countries = countries_geo.sort_values("hosts", ascending=False).head(12)
    for row in top_countries.itertuples(index=False):
        width = min(4.0, 0.4 + math.log1p(float(row.hosts)) * 0.65)
        ax.plot(
            [source_lon, float(row.longitude)],
            [source_lat, float(row.latitude)],
            color="#8b1e3f",
            alpha=0.25,
            linewidth=width,
            zorder=1,
        )

    ax.scatter(
        host_points["longitude"],
        host_points["latitude"],
        s=22,
        color="#376996",
        alpha=0.62,
        edgecolors="white",
        linewidths=0.35,
        label="Hosts contactados",
        zorder=3,
    )

    country_sizes = 35 + (countries_geo["hosts"].astype(float) ** 0.82) * 18
    ax.scatter(
        countries_geo["longitude"],
        countries_geo["latitude"],
        s=country_sizes,
        color="#c43c3c",
        alpha=0.72,
        edgecolors="#263238",
        linewidths=0.5,
        label="Agregado por pais",
        zorder=4,
    )
    ax.scatter([source_lon], [source_lat], s=180, color="#111111", marker="*", label="Proceso en sandbox", zorder=5)

    for row in top_countries.itertuples(index=False):
        ax.annotate(
            f"{row.country} ({int(row.hosts)})",
            (float(row.longitude), float(row.latitude)),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
            zorder=6,
        )

    ax.legend(loc="lower left")
    note = "Coordenadas aproximadas por centroide de pais; puntos de host dispersados solo para evitar superposicion visual."
    ax.text(-178, -56, note, fontsize=8, color="#555555")
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Construye un grafo geografico realista con hosts de Hybrid Analysis.")
    parser.add_argument("--hosts", type=Path, default=DEFAULT_HOSTS)
    parser.add_argument("--countries", type=Path, default=DEFAULT_COUNTRIES)
    parser.add_argument("--host-graphml", type=Path, default=DEFAULT_HOST_GRAPHML)
    parser.add_argument("--country-graphml", type=Path, default=DEFAULT_COUNTRY_GRAPHML)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--figure", type=Path, default=DEFAULT_FIGURE)
    args = parser.parse_args()

    hosts, countries = load_inputs(args.hosts, args.countries)
    host_graph = build_host_graph(hosts)
    country_graph = build_country_graph(countries)

    args.host_graphml.parent.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(host_graph, args.host_graphml)
    nx.write_graphml(country_graph, args.country_graphml)
    plot_geo_graph(hosts, countries, args.figure)

    metadata = {
        "inputs": {
            "hosts": str(args.hosts),
            "countries": str(args.countries),
        },
        "host_graph": {
            "nodes": host_graph.number_of_nodes(),
            "edges": host_graph.number_of_edges(),
            "graphml": str(args.host_graphml),
        },
        "country_graph": {
            "nodes": country_graph.number_of_nodes(),
            "edges": country_graph.number_of_edges(),
            "graphml": str(args.country_graphml),
        },
        "figure": str(args.figure),
        "coordinate_method": "country centroid with deterministic visual jitter for host-level nodes",
        "top_countries": countries.sort_values("hosts", ascending=False).head(10).to_dict(orient="records"),
    }
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    with args.metadata.open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2, ensure_ascii=False)

    print(json.dumps(metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
