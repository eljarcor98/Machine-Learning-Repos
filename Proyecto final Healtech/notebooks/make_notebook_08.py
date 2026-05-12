"""Genera notebooks/08_dashboard_interactivo.ipynb — ipywidgets + matplotlib."""
import json, textwrap, uuid
from pathlib import Path

def _id(): return str(uuid.uuid4())[:8]
def md(s): return {"cell_type":"markdown","id":_id(),"metadata":{},"source":s.strip().splitlines(True)}
def code(s): return {"cell_type":"code","id":_id(),"execution_count":None,"metadata":{},"outputs":[],"source":textwrap.dedent(s).strip().splitlines(True)}

cells = []

cells.append(md("""# 🏥 Dashboard Interactivo — WannaCry Pandemia de Red
Controla en tiempo real β, γ y el escenario. El panel se actualiza automáticamente.
"""))

cells.append(code("""
import matplotlib
matplotlib.use('Agg')
import sys, json, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mtick
import matplotlib.patches as mpatches
import networkx as nx
import ipywidgets as widgets
from IPython.display import display
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path("..").resolve()))
from src.simulation.epidemic_models import run_sir_simulation, run_seir_simulation

ROOT      = Path("..").resolve()
PROCESSED = ROOT / "data" / "processed"

with open(PROCESSED / "wannacry_pcap_sir_metadata.json") as f:
    meta = json.load(f)

BETA_BASE  = meta["beta_from_pcap"]
GAMMA_BASE = meta["baseline_gamma"]
BETA_KS    = meta["contained_beta"]
GAMMA_KS   = meta["contained_gamma"]

N    = 300
SEED = 42
G_raw = nx.barabasi_albert_graph(N, 3, seed=SEED)
G     = nx.relabel_nodes(G_raw, {n: f"Host_{n:03d}" for n in G_raw.nodes()})
INIT  = ["Host_004"]
POS   = nx.spring_layout(G, seed=SEED, k=0.3)
DEGS  = dict(G.degree())

BG, CARD, EDGE = "#0D1117", "#161B22", "#30363D"
CS, CI, CR = "#74B9FF", "#FF7675", "#55EFC4"

print("Librerias cargadas. Grafo listo: {} nodos, {} aristas.".format(
    G.number_of_nodes(), G.number_of_edges()))
"""))

cells.append(md("## 🎛️ Controles del Dashboard"))

cells.append(code("""
# ── Widgets ──────────────────────────────────────────────────────────────────
w_scenario = widgets.ToggleButtons(
    options=["Sin Contencion", "Kill-Switch", "SEIR", "Manual"],
    value="Sin Contencion",
    description="Escenario:",
    button_style="info",
    style={"button_width": "130px"},
)
w_beta  = widgets.FloatSlider(value=BETA_BASE, min=0.01, max=1.0,  step=0.01,
    description="β (transmision):", style={"description_width":"150px"},
    layout=widgets.Layout(width="500px"), readout_format=".2f")
w_gamma = widgets.FloatSlider(value=GAMMA_BASE, min=0.01, max=0.5, step=0.01,
    description="γ (recuperacion):", style={"description_width":"150px"},
    layout=widgets.Layout(width="500px"), readout_format=".2f")
w_sigma = widgets.FloatSlider(value=0.5, min=0.05, max=1.0, step=0.05,
    description="σ (latencia SEIR):", style={"description_width":"150px"},
    layout=widgets.Layout(width="500px"), readout_format=".2f")
w_steps = widgets.IntSlider(value=80, min=20, max=200, step=5,
    description="Pasos:", style={"description_width":"150px"},
    layout=widgets.Layout(width="500px"))
w_show_graph = widgets.Checkbox(value=True, description="Mostrar grafo final",
    style={"description_width":"150px"})

panel_controls = widgets.VBox([
    w_scenario,
    widgets.HBox([widgets.VBox([w_beta, w_gamma, w_sigma]),
                  widgets.VBox([w_steps, w_show_graph])]),
])
display(panel_controls)
"""))

cells.append(md("## 📊 Panel de Visualización"))

cells.append(code("""
# ── Output area ──────────────────────────────────────────────────────────────
out = widgets.Output()

def style_ax(ax, title, fontsize=11):
    ax.set_facecolor(CARD)
    ax.set_title(title, color="white", fontsize=fontsize, fontweight="bold", pad=7)
    ax.tick_params(colors="#DFE6E9", labelsize=8)
    for sp in ax.spines.values(): sp.set_edgecolor(EDGE)
    ax.grid(alpha=0.12, color="#636e72")

def run_scenario(scenario, beta, gamma, sigma, steps):
    if scenario == "Sin Contencion":
        b, g = BETA_BASE, GAMMA_BASE
        res = run_sir_simulation(G, beta=b, gamma=g, steps=steps, initial_infected=INIT)
        df = res.history.copy(); df["E"] = 0
        label = f"SIR sin contencion (b={b}, g={g})"
    elif scenario == "Kill-Switch":
        b, g = BETA_KS, GAMMA_KS
        res = run_sir_simulation(G, beta=b, gamma=g, steps=steps, initial_infected=INIT)
        df = res.history.copy(); df["E"] = 0
        label = f"SIR kill-switch (b={b}, g={g})"
    elif scenario == "SEIR":
        b, g = BETA_BASE, GAMMA_BASE
        res = run_seir_simulation(G, beta=b, sigma=sigma, gamma=g,
                                  steps=steps, initial_infected=INIT)
        df = res.history.copy()
        if "E" not in df.columns: df["E"] = 0
        label = f"SEIR (b={b}, sigma={sigma}, g={g})"
    else:
        b, g = beta, gamma
        res = run_sir_simulation(G, beta=b, gamma=g, steps=steps, initial_infected=INIT)
        df = res.history.copy(); df["E"] = 0
        label = f"Manual (b={b:.2f}, g={g:.2f})"
    return df, res.node_states, b, g, label

def update_dashboard(change=None):
    scenario = w_scenario.value
    beta     = w_beta.value
    gamma    = w_gamma.value
    sigma    = w_sigma.value
    steps    = w_steps.value
    show_g   = w_show_graph.value

    df, node_states, b, g, label = run_scenario(scenario, beta, gamma, sigma, steps)

    r0  = round(b / g, 2)
    pico_row = df.loc[df["I"].idxmax()]
    pico_step = int(pico_row["step"])
    pico_pct  = pico_row["I"] / N
    tasa_final = df.iloc[-1]["R"] / N
    df["Rt"]  = (b / g) * (df["S"] / N)
    df["dI"]  = df["I"].diff().fillna(0)

    # ── Crear figura nueva en cada llamada ──────────────────────────────────
    out.clear_output(wait=True)
    ncols = 3 if show_g else 2
    fig, _ = plt.subplots(1, 1)  # placeholder; usamos gridspec manual
    plt.close(fig)
    fig = plt.figure(figsize=(20, 16))
    fig.patch.set_facecolor(BG)
    gs = gridspec.GridSpec(2, ncols, figure=fig, hspace=0.45, wspace=0.32)

    # ── 1. Curva SIR principal ───────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, :2])
    style_ax(ax1, f"Curva SIR/SEIR — {label}   |   R0 = {r0}", 12)
    t = df["step"]
    ax1.fill_between(t, df["S"]/N*100, alpha=0.12, color=CS)
    ax1.fill_between(t, df["I"]/N*100, alpha=0.18, color=CI)
    ax1.fill_between(t, df["R"]/N*100, alpha=0.12, color=CR)
    ax1.plot(t, df["S"]/N*100, color=CS, lw=2.2, label="Susceptibles (S)")
    ax1.plot(t, df["I"]/N*100, color=CI, lw=2.2, label="Infectados (I)")
    ax1.plot(t, df["R"]/N*100, color=CR, lw=2.2, label="Recuperados (R)")
    if "E" in df.columns and df["E"].max() > 0:
        ax1.plot(t, df["E"]/N*100, color="#FDCB6E", lw=1.8, ls="--", label="Expuestos (E)")
    ax1.axvline(pico_step, color=CI, ls="--", lw=1.5,
                label=f"Pico: paso {pico_step} ({pico_pct:.0%})")
    ax1.scatter(pico_step, pico_pct*100, color="white", s=100, zorder=7)
    ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax1.set_xlabel("Paso temporal", color="#DFE6E9")
    ax1.set_ylabel("% Nodos", color="#DFE6E9")
    ax1.legend(fontsize=8, facecolor=BG, labelcolor="white", loc="center right")

    # ── 2. R(t) ─────────────────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, -1])
    style_ax(ax2, "R(t) — Numero Reproductivo")
    ax2.plot(df["step"], df["Rt"], color="#E17055", lw=2)
    ax2.axhline(1.0, color="#FDCB6E", ls="--", lw=1.5, label="R(t)=1")
    ax2.fill_between(df["step"], df["Rt"], 1,
                     where=df["Rt"]>1, alpha=0.2, color="#E17055")
    ax2.fill_between(df["step"], df["Rt"], 1,
                     where=df["Rt"]<1, alpha=0.2, color="#00B894")
    ax2.set_xlabel("Paso", color="#DFE6E9")
    ax2.set_ylabel("R(t)", color="#DFE6E9")
    ax2.legend(fontsize=8, facecolor=BG, labelcolor="white")

    # ── 3. Velocidad dI/dt ───────────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 0])
    style_ax(ax3, "Velocidad dI/dt")
    cols_bar = [CI if v >= 0 else CR for v in df["dI"]]
    ax3.bar(df["step"], df["dI"], color=cols_bar, width=1, alpha=0.8)
    ax3.axhline(0, color="white", lw=0.8)
    ax3.set_xlabel("Paso", color="#DFE6E9")
    ax3.set_ylabel("Nuevos inf./paso", color="#DFE6E9")

    # ── 4. Metricas clinicas ─────────────────────────────────────────────────
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_facecolor(CARD)
    ax4.axis("off")
    r0_color = "#FF7675" if r0 > 1 else "#55EFC4"
    cont_thr = r0 / (1 + r0)
    lines = [
        ("R\u2080 base",            f"{r0:.2f}",             r0_color),
        ("Pico infeccion",        f"{pico_pct:.1%}  (paso {pico_step})", "#FF7675"),
        ("Tasa ataque final",     f"{tasa_final:.1%}",     "#FDCB6E"),
        ("Nodos salvados",        f"{int((1-tasa_final)*N)}/{N}", "#55EFC4"),
        ("R(t)<1 desde paso",     str(int(df[df['Rt']<1]['step'].min()))
                                  if (df['Rt']<1).any() else "nunca",
                                  "#74B9FF"),
        ("Umbral contencion",     f"sensibilidad > {cont_thr:.1%}", "#B2BEC3"),
        ("Beta / Gamma",          f"{b:.3f} / {g:.3f}",    "#DFE6E9"),
    ]
    ax4.set_title("Indicadores Clinicos", color="white", fontsize=11,
                  fontweight="bold", pad=7)
    for i, (name, val, col) in enumerate(lines):
        y = 0.92 - i*0.13
        ax4.text(0.02, y, name + ":", color="#B2BEC3", fontsize=10,
                 transform=ax4.transAxes, va="top")
        ax4.text(0.55, y, val, color=col, fontsize=10, fontweight="bold",
                 transform=ax4.transAxes, va="top")

    # ── 5. Grafo (opcional) ──────────────────────────────────────────────────
    if show_g:
        ax5 = fig.add_subplot(gs[1, 2])
        ax5.set_facecolor(CARD)
        ax5.set_title("Estado Final del Grafo", color="white", fontsize=11,
                      fontweight="bold", pad=7)
        ncolors = [{"S":CS,"I":CI,"R":CR,"E":"#FDCB6E"}.get(
                    node_states.get(n,"S"), CS) for n in G.nodes()]
        nsizes  = [max(15, DEGS.get(n,1)*8) for n in G.nodes()]
        nx.draw_networkx(G, pos=POS, ax=ax5, with_labels=False,
                         node_color=ncolors, node_size=nsizes,
                         edge_color=EDGE, width=0.3, alpha=0.85)
        ax5.legend(handles=[mpatches.Patch(color=CS,label="S"),
                             mpatches.Patch(color=CI,label="I"),
                             mpatches.Patch(color=CR,label="R")],
                   fontsize=8, facecolor=BG, labelcolor="white", loc="upper left")
        ax5.axis("off")

    fig.suptitle("Dashboard WannaCry — Pandemia de Red | Parametros PCAP real 15/05/2017",
                 color="white", fontsize=13, fontweight="bold")
    plt.tight_layout()
    with out:
        plt.show()
    plt.close(fig)

# Conectar widgets y mostrar
for w in [w_scenario, w_beta, w_gamma, w_sigma, w_steps, w_show_graph]:
    w.observe(update_dashboard, names="value")

display(out)
update_dashboard()
"""))

cells.append(md("## 💾 Guardar Snapshot del Estado Actual"))
cells.append(code("""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

out_path = Path("..") / "reports" / "figures" / "08_dashboard_snapshot.png"
# Re-ejecuta la simulacion con los valores actuales de los sliders
df_snap, ns_snap, b_snap, g_snap, lbl_snap = run_scenario(
    w_scenario.value, w_beta.value, w_gamma.value, w_sigma.value, w_steps.value)
pico = df_snap.loc[df_snap["I"].idxmax()]
df_snap["Rt"] = (b_snap/g_snap)*(df_snap["S"]/N)
df_snap["dI"] = df_snap["I"].diff().fillna(0)

fig_s = plt.figure(figsize=(20, 14))
fig_s.patch.set_facecolor(BG)
gs_s  = gridspec.GridSpec(2, 3, figure=fig_s, hspace=0.45, wspace=0.32)

ax1s = fig_s.add_subplot(gs_s[0, :2])
ax1s.set_facecolor(CARD); ax1s.set_title(f"Curva SIR | {lbl_snap}", color="white", fontweight="bold")
t = df_snap["step"]
ax1s.plot(t, df_snap["S"]/N*100, color=CS, lw=2, label="S")
ax1s.plot(t, df_snap["I"]/N*100, color=CI, lw=2, label="I")
ax1s.plot(t, df_snap["R"]/N*100, color=CR, lw=2, label="R")
ax1s.axvline(pico["step"], color=CI, ls="--", lw=1.5)
ax1s.set_xlabel("Paso", color="#DFE6E9"); ax1s.set_ylabel("% Nodos", color="#DFE6E9")
ax1s.legend(facecolor=BG, labelcolor="white", fontsize=9)
for sp in ax1s.spines.values(): sp.set_edgecolor(EDGE)

ax2s = fig_s.add_subplot(gs_s[0, 2])
ax2s.set_facecolor(CARD); ax2s.set_title("R(t)", color="white", fontweight="bold")
ax2s.plot(df_snap["step"], df_snap["Rt"], color="#E17055", lw=2)
ax2s.axhline(1.0, color="#FDCB6E", ls="--"); ax2s.set_xlabel("Paso", color="#DFE6E9")
for sp in ax2s.spines.values(): sp.set_edgecolor(EDGE)

ax3s = fig_s.add_subplot(gs_s[1, 0])
ax3s.set_facecolor(CARD); ax3s.set_title("Velocidad dI/dt", color="white", fontweight="bold")
ax3s.bar(df_snap["step"], df_snap["dI"], color=[CI if v>=0 else CR for v in df_snap["dI"]], width=1)
for sp in ax3s.spines.values(): sp.set_edgecolor(EDGE)

ax4s = fig_s.add_subplot(gs_s[1, 1])
ax4s.set_facecolor(CARD); ax4s.axis("off")
r0_s = round(b_snap/g_snap, 2)
ax4s.set_title("Indicadores Clinicos", color="white", fontweight="bold")
for i,(nm,vl,cl) in enumerate([
    ("R0", f"{r0_s}", "#FF7675" if r0_s>1 else "#55EFC4"),
    ("Pico", f"{pico['I']/N:.1%} paso {int(pico['step'])}", CI),
    ("Ataque final", f"{df_snap.iloc[-1]['R']/N:.1%}", "#FDCB6E"),
]):
    ax4s.text(0.02, 0.88-i*0.18, nm+":", color="#B2BEC3", fontsize=11, transform=ax4s.transAxes)
    ax4s.text(0.55, 0.88-i*0.18, vl, color=cl, fontsize=11, fontweight="bold", transform=ax4s.transAxes)

ax5s = fig_s.add_subplot(gs_s[1, 2])
ax5s.set_facecolor(CARD); ax5s.set_title("Grafo Final", color="white", fontweight="bold")
import matplotlib.patches as mpatches
ncolors = [{"S":CS,"I":CI,"R":CR,"E":"#FDCB6E"}.get(ns_snap.get(n,"S"),CS) for n in G.nodes()]
nx.draw_networkx(G, pos=POS, ax=ax5s, with_labels=False, node_color=ncolors,
                 node_size=[max(15,DEGS.get(n,1)*8) for n in G.nodes()],
                 edge_color=EDGE, width=0.3, alpha=0.85)
ax5s.legend(handles=[mpatches.Patch(color=CS,label="S"),
                      mpatches.Patch(color=CI,label="I"),
                      mpatches.Patch(color=CR,label="R")],
            facecolor=BG, labelcolor="white", fontsize=8, loc="upper left")
ax5s.axis("off")

fig_s.suptitle("Dashboard WannaCry — Snapshot", color="white", fontsize=13, fontweight="bold")
fig_s.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=BG)
plt.close(fig_s)
print(f"Guardado en: {out_path.resolve()}")
"""))

nb = {
    "nbformat": 4, "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name":"Python (HealTech)","language":"python","name":"healtech_venv"},
        "language_info": {"name":"python","version":"3.12.0"},
    },
    "cells": cells,
}
out = Path(__file__).parent / "08_dashboard_interactivo.ipynb"
out.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"[OK] {out}")
