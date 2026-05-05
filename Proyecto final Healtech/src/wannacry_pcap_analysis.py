from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


DEFAULT_FLOWS = Path("data/processed/wannacry_flows.csv")
DEFAULT_SUMMARY = Path("data/processed/wannacry_pcap_summary.json")
DEFAULT_OUTPUT_DIR = Path("reports/figures")
DEFAULT_ANALYSIS = Path("data/processed/wannacry_pcap_analysis.json")


def load_flows(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"No existe {path}. Primero ejecuta src/data/parse_wannacry_pcap.py."
        )
    df = pd.read_csv(path)
    for column in ["src_port", "dst_port", "packets", "bytes", "first_seen", "last_seen"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def build_graph(df: pd.DataFrame) -> nx.DiGraph:
    graph = nx.DiGraph()
    for row in df.itertuples(index=False):
        src = str(row.src_ip)
        dst = str(row.dst_ip)
        if src == "nan" or dst == "nan":
            continue
        graph.add_edge(
            src,
            dst,
            protocol=row.protocol,
            src_port=None if pd.isna(row.src_port) else int(row.src_port),
            dst_port=None if pd.isna(row.dst_port) else int(row.dst_port),
            packets=int(row.packets),
            bytes=int(row.bytes),
            is_smb=bool(row.src_port == 445 or row.dst_port == 445),
        )
    return graph


def summarize_flows(df: pd.DataFrame, pcap_summary: dict[str, object] | None = None) -> dict[str, object]:
    smb = df[(df["src_port"] == 445) | (df["dst_port"] == 445)]
    duration = None
    if pcap_summary:
        duration = pcap_summary.get("duration_seconds")
    if duration is None or not duration:
        duration = float(df["last_seen"].max() - df["first_seen"].min())

    total_packets = int(df["packets"].sum())
    smb_packets = int(smb["packets"].sum())
    total_flows = int(len(df))
    smb_flows = int(len(smb))

    return {
        "flows": total_flows,
        "smb_flows": smb_flows,
        "smb_flow_share": round(smb_flows / total_flows, 6) if total_flows else 0,
        "packets": total_packets,
        "smb_packets": smb_packets,
        "smb_packet_share": round(smb_packets / total_packets, 6) if total_packets else 0,
        "unique_ips": int(pd.concat([df["src_ip"], df["dst_ip"]]).nunique()),
        "unique_src_ips": int(df["src_ip"].nunique()),
        "unique_dst_ips": int(df["dst_ip"].nunique()),
        "duration_seconds": round(float(duration), 6) if duration else 0,
        "observed_packet_rate_per_second": round(total_packets / duration, 6) if duration else None,
        "observed_smb_packet_rate_per_second": round(smb_packets / duration, 6) if duration else None,
        "top_dst_ports": {
            str(int(port)): int(count)
            for port, count in df.groupby("dst_port")["packets"].sum().sort_values(ascending=False).head(15).items()
            if not pd.isna(port)
        },
    }


def plot_top_ports(df: pd.DataFrame, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    top_ports = df.groupby("dst_port")["packets"].sum().sort_values(ascending=False).head(12)
    labels = [str(int(port)) for port in top_ports.index]

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#c43c3c" if label == "445" else "#376996" for label in labels]
    ax.bar(labels, top_ports.values, color=colors)
    ax.set_title("WannaCry PCAP - paquetes por puerto destino")
    ax.set_xlabel("Puerto destino")
    ax.set_ylabel("Paquetes")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()

    output_path = output_dir / "wannacry_pcap_top_ports.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_graph(graph: nx.DiGraph, output_dir: Path, max_edges: int = 80) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    edges = sorted(graph.edges(data=True), key=lambda item: item[2].get("packets", 0), reverse=True)[:max_edges]
    subgraph = nx.DiGraph()
    subgraph.add_edges_from((u, v, data) for u, v, data in edges)

    fig, ax = plt.subplots(figsize=(11, 7))
    pos = nx.spring_layout(subgraph, seed=42, weight="packets")
    edge_colors = ["#c43c3c" if data.get("is_smb") else "#6f7f8f" for _, _, data in subgraph.edges(data=True)]
    edge_widths = [max(1.0, min(5.0, data.get("packets", 1) ** 0.25)) for _, _, data in subgraph.edges(data=True)]

    nx.draw_networkx_nodes(subgraph, pos, node_color="#f2c14e", node_size=850, edgecolors="#263238", ax=ax)
    nx.draw_networkx_edges(
        subgraph,
        pos,
        edge_color=edge_colors,
        width=edge_widths,
        alpha=0.75,
        arrows=True,
        arrowsize=16,
        ax=ax,
    )
    nx.draw_networkx_labels(subgraph, pos, font_size=9, ax=ax)
    ax.set_title("WannaCry PCAP - grafo observado de comunicaciones")
    ax.axis("off")
    fig.tight_layout()

    output_path = output_dir / "wannacry_pcap_observed_graph.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def read_json(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analiza flujos extraidos del PCAP de WannaCry.")
    parser.add_argument("--flows", type=Path, default=DEFAULT_FLOWS)
    parser.add_argument("--pcap-summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--analysis", type=Path, default=DEFAULT_ANALYSIS)
    args = parser.parse_args()

    df = load_flows(args.flows)
    pcap_summary = read_json(args.pcap_summary)
    graph = build_graph(df)
    summary = summarize_flows(df, pcap_summary)
    summary["graph"] = {
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "density": nx.density(graph) if graph.number_of_nodes() > 1 else 0,
        "top_degree_nodes": sorted(graph.degree, key=lambda item: item[1], reverse=True)[:10],
    }
    summary["figures"] = {
        "top_ports": str(plot_top_ports(df, args.output_dir)),
        "observed_graph": str(plot_graph(graph, args.output_dir)),
    }

    args.analysis.parent.mkdir(parents=True, exist_ok=True)
    with args.analysis.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
