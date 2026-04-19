from __future__ import annotations

from dataclasses import dataclass
import random

import networkx as nx
import pandas as pd


@dataclass
class SimulationResult:
    history: pd.DataFrame
    node_states: dict[str, str]


def _initialize_states(
    graph: nx.Graph,
    initial_infected: list[str] | None = None,
    initial_exposed: list[str] | None = None,
) -> dict[str, str]:
    states = {str(node): "S" for node in graph.nodes}

    for node in initial_exposed or []:
        if node in graph:
            states[str(node)] = "E"

    for node in initial_infected or []:
        if node in graph:
            states[str(node)] = "I"

    return states


def _count_states(states: dict[str, str]) -> dict[str, int]:
    counts = {"S": 0, "E": 0, "I": 0, "R": 0}
    for state in states.values():
        counts[state] = counts.get(state, 0) + 1
    return counts


def run_sir_simulation(
    graph: nx.Graph,
    beta: float,
    gamma: float,
    steps: int,
    initial_infected: list[str] | None = None,
    seed: int = 42,
) -> SimulationResult:
    random.seed(seed)
    states = _initialize_states(graph, initial_infected=initial_infected)
    history = []

    for step in range(steps + 1):
        counts = _count_states(states)
        history.append({"step": step, **counts})

        if step == steps:
            break

        updated_states = states.copy()
        for node in graph.nodes:
            current_state = states[str(node)]

            if current_state == "I":
                for neighbor in graph.neighbors(node):
                    if states[str(neighbor)] == "S" and random.random() < beta:
                        updated_states[str(neighbor)] = "I"

                if random.random() < gamma:
                    updated_states[str(node)] = "R"

        states = updated_states

    return SimulationResult(history=pd.DataFrame(history), node_states=states)


def run_seir_simulation(
    graph: nx.Graph,
    beta: float,
    sigma: float,
    gamma: float,
    steps: int,
    initial_infected: list[str] | None = None,
    initial_exposed: list[str] | None = None,
    seed: int = 42,
) -> SimulationResult:
    random.seed(seed)
    states = _initialize_states(
        graph,
        initial_infected=initial_infected,
        initial_exposed=initial_exposed,
    )
    history = []

    for step in range(steps + 1):
        counts = _count_states(states)
        history.append({"step": step, **counts})

        if step == steps:
            break

        updated_states = states.copy()
        for node in graph.nodes:
            current_state = states[str(node)]

            if current_state == "I":
                for neighbor in graph.neighbors(node):
                    if states[str(neighbor)] == "S" and random.random() < beta:
                        updated_states[str(neighbor)] = "E"

                if random.random() < gamma:
                    updated_states[str(node)] = "R"

            elif current_state == "E":
                if random.random() < sigma:
                    updated_states[str(node)] = "I"

        states = updated_states

    return SimulationResult(history=pd.DataFrame(history), node_states=states)
