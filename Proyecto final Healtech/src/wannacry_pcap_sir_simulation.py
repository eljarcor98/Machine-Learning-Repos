from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


DEFAULT_ANALYSIS = Path("data/processed/wannacry_pcap_analysis.json")
DEFAULT_OUTPUT_DIR = Path("reports/figures")
DEFAULT_RESULTS = Path("data/processed/wannacry_pcap_sir_results.csv")
DEFAULT_METADATA = Path("data/processed/wannacry_pcap_sir_metadata.json")


def load_analysis(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(
            f"No existe {path}. Ejecuta primero src/wannacry_pcap_analysis.py."
        )
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def beta_from_pcap(analysis: dict[str, object]) -> float:
    smb_share = float(analysis.get("smb_packet_share", 0.0))
    packet_rate = float(analysis.get("observed_smb_packet_rate_per_second", 0.0) or 0.0)

    # Alta presencia de SMB + alta tasa observada = comportamiento de gusano.
    share_component = 0.25 + (0.65 * smb_share)
    rate_component = min(0.05, packet_rate / 100_000)
    return round(min(0.95, share_component + rate_component), 4)


def make_enterprise_like_graph(nodes: int, seed: int) -> nx.Graph:
    graph = nx.barabasi_albert_graph(nodes, 3, seed=seed)
    return nx.relabel_nodes(graph, {node: f"Host_{node:03d}" for node in graph.nodes})


def run_dynamic_sir(
    graph: nx.Graph,
    beta: float,
    gamma: float,
    steps: int,
    initial_infected: list[str],
    kill_switch_step: int | None = None,
    contained_beta: float | None = None,
    contained_gamma: float | None = None,
    seed: int = 42,
) -> pd.DataFrame:
    random.seed(seed)
    states = {node: "S" for node in graph.nodes}
    for node in initial_infected:
        if node in states:
            states[node] = "I"

    history: list[dict[str, int | float | str]] = []
    for step in range(steps + 1):
        current_beta = beta
        current_gamma = gamma
        if kill_switch_step is not None and step >= kill_switch_step:
            current_beta = contained_beta if contained_beta is not None else beta
            current_gamma = contained_gamma if contained_gamma is not None else gamma

        counts = {
            "S": sum(1 for state in states.values() if state == "S"),
            "I": sum(1 for state in states.values() if state == "I"),
            "R": sum(1 for state in states.values() if state == "R"),
        }
        history.append(
            {
                "step": step,
                "S": counts["S"],
                "I": counts["I"],
                "R": counts["R"],
                "beta": current_beta,
                "gamma": current_gamma,
            }
        )

        if step == steps:
            break

        updated = states.copy()
        for node in graph.nodes:
            if states[node] == "I":
                for neighbor in graph.neighbors(node):
                    if states[neighbor] == "S" and random.random() < current_beta:
                        updated[neighbor] = "I"
                if random.random() < current_gamma:
                    updated[node] = "R"
        states = updated

    return pd.DataFrame(history)


def plot_scenarios(no_containment: pd.DataFrame, kill_switch: pd.DataFrame, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

    scenarios = [
        ("Sin contencion", no_containment),
        ("Con kill-switch y aislamiento", kill_switch),
    ]
    colors = {"S": "#376996", "I": "#c43c3c", "R": "#2f855a"}
    labels = {"S": "Susceptibles", "I": "Infectados", "R": "Recuperados/Aislados"}

    for ax, (title, df) in zip(axes, scenarios):
        for state in ["S", "I", "R"]:
            ax.plot(df["step"], df[state], label=labels[state], color=colors[state], linewidth=2)
        peak = df.loc[df["I"].idxmax()]
        ax.scatter([peak["step"]], [peak["I"]], color="#111111", zorder=5)
        ax.annotate(
            f"Pico: {int(peak['I'])}",
            xy=(peak["step"], peak["I"]),
            xytext=(8, -18),
            textcoords="offset points",
            fontsize=9,
        )
        ax.set_title(title)
        ax.set_xlabel("Paso temporal")
        ax.grid(alpha=0.25)

    axes[0].set_ylabel("Cantidad de equipos")
    axes[1].legend(loc="upper right")
    fig.suptitle("Simulacion SIR informada por PCAP de WannaCry", fontweight="bold")
    fig.tight_layout()

    output_path = output_dir / "wannacry_pcap_informed_sir.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Simula WannaCry con parametros informados por PCAP.")
    parser.add_argument("--analysis", type=Path, default=DEFAULT_ANALYSIS)
    parser.add_argument("--nodes", type=int, default=300)
    parser.add_argument("--steps", type=int, default=80)
    parser.add_argument("--kill-switch-step", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    args = parser.parse_args()

    analysis = load_analysis(args.analysis)
    beta = beta_from_pcap(analysis)
    gamma = 0.04
    graph = make_enterprise_like_graph(args.nodes, args.seed)
    patient_zero = [max(graph.degree, key=lambda item: item[1])[0]]

    no_containment = run_dynamic_sir(
        graph,
        beta=beta,
        gamma=gamma,
        steps=args.steps,
        initial_infected=patient_zero,
        seed=args.seed,
    )
    no_containment["scenario"] = "sin_contencion"

    kill_switch = run_dynamic_sir(
        graph,
        beta=beta,
        gamma=gamma,
        steps=args.steps,
        initial_infected=patient_zero,
        kill_switch_step=args.kill_switch_step,
        contained_beta=0.08,
        contained_gamma=0.22,
        seed=args.seed,
    )
    kill_switch["scenario"] = "kill_switch"

    results = pd.concat([no_containment, kill_switch], ignore_index=True)
    args.results.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.results, index=False)

    figure = plot_scenarios(no_containment, kill_switch, args.output_dir)

    metadata = {
        "pcap_analysis": str(args.analysis),
        "nodes": args.nodes,
        "edges": graph.number_of_edges(),
        "seed": args.seed,
        "initial_infected": patient_zero,
        "beta_from_pcap": beta,
        "baseline_gamma": gamma,
        "kill_switch_step": args.kill_switch_step,
        "contained_beta": 0.08,
        "contained_gamma": 0.22,
        "figure": str(figure),
        "results": str(args.results),
        "pcap_smb_packet_share": analysis.get("smb_packet_share"),
        "observed_smb_packet_rate_per_second": analysis.get("observed_smb_packet_rate_per_second"),
    }
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    with args.metadata.open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2, ensure_ascii=False)

    print(json.dumps(metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
