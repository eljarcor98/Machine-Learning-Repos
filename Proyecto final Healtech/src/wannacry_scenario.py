import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from pipeline_complete import DataReader, NetworkGraph, SIRSimulator, ProjectConfig

class WannaCryConfig(ProjectConfig):
    """Configuración específica para simular el comportamiento de WannaCry"""
    # WannaCry se caracterizó por una propagación extremadamente rápida gracias 
    # a la vulnerabilidad EternalBlue (SMBv1), actuando como gusano autónomo.
    BETA = 0.90          # Alta tasa de transmisión (infección casi segura si hay contacto y vulnerabilidad)
    
    # La recuperación es muy baja porque una vez cifrado, el equipo no se recupera 
    # sin una clave o restauración de backup. Solo se aislarían los equipos una vez detectado.
    GAMMA = 0.05         # Baja tasa de recuperación/aislamiento temprano
    
    TIME_STEPS = 100     # La infección fue tan rápida que en pocas horas alcanzó su pico mundial
    
def main():
    print("="*80)
    print("PIPELINE DE ANÁLISIS: Escenario WannaCry")
    print("="*80)
    
    config = WannaCryConfig()
    
    # ---------- Paso 1 & 2: Grafo Sintético para Simulación Rápida ----------
    print("\n[1/2] Construyendo grafo de red...")
    net = NetworkGraph(name="Red Vulnerable (SMBv1)")
    
    # Crear un grafo demo más grande para ver bien la propagación
    # Topología tipo Barabasi-Albert (Scale-free) que representa mejor una red real
    import networkx as nx
    G_sim = nx.barabasi_albert_graph(200, 3) 
    
    for u, v in G_sim.edges():
        net.add_edge_from_flow(f"Host_{u}", f"Host_{v}")
        
    stats = net.get_stats()
    print(f"  -> {stats['nodes']} nodos, {stats['edges']} aristas creadas")
    
    # ---------- Paso 3: Ejecutar simulación SIR ----------
    print("\n[3/3] Ejecutando simulación SIR (Comportamiento WannaCry)...")
    
    # Simular un único paciente cero (como ocurrió en la realidad)
    initial_infected = ["Host_0"] 
    
    sir = SIRSimulator(net, beta=config.BETA, gamma=config.GAMMA, days=config.SIM_DAYS)
    history = sir.run(initial_infected=initial_infected, timesteps=config.TIME_STEPS)
    
    # ---------- Generando reportes ----------
    net.visualize(output_file=config.REPORTS / 'wannacry_network_graph.png')
    
    # Plot personalizado para WannaCry
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(history['time'], history['S'], 'b-', label='Susceptibles (Vulnerables)', linewidth=2)
    ax.plot(history['time'], history['I'], 'r-', label='Infectados (Cifrados)', linewidth=2)
    ax.plot(history['time'], history['R'], 'g-', label='Recuperados (Parcheados/Aislados)', linewidth=2)
    
    ax.set_xlabel('Tiempo (Horas/Ciclos)', fontsize=12)
    ax.set_ylabel('Cantidad de Equipos', fontsize=12)
    ax.set_title('Simulación SIR - Propagación de Ransomware tipo WannaCry', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    output_sir = config.REPORTS / 'wannacry_sir_simulation.png'
    fig.savefig(output_sir, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"-> Simulación guardada en: {output_sir}")
    print("\n" + "="*80)
    print("[OK] ESCENARIO WANNACRY COMPLETADO")
    print("="*80)

if __name__ == '__main__':
    main()
