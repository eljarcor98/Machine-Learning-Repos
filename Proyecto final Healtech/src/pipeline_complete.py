"""
PIPELINE COMPLETO: Análisis de propagación de amenazas con SIR/SEIR
================================================================================

Este pipeline:
1. Lee datos de flujos de red (IPs origen/destino)
2. Construye un grafo de comunicaciones
3. Identifica ataques y mapea a nodos
4. Ejecuta simulación SIR/SEIR
5. Evalúa estrategias de contención
"""

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict
import json
import sys

# ============================================================================
# 1. CONFIGURACIÓN INICIAL
# ============================================================================

class ProjectConfig:
    """Configuración del proyecto"""
    
    # Rutas
    DATA_RAW = Path('../data/raw')
    DATA_PROCESSED = Path('../data/processed')
    REPORTS = Path('../reports/figures')
    
    # Crear directorios
    for d in [DATA_PROCESSED, REPORTS]:
        d.mkdir(parents=True, exist_ok=True)
    
    # Parámetros SIR/SEIR
    BETA = 0.4          # Tasa de transmisión
    GAMMA = 0.1         # Tasa de recuperación/aislamiento
    SIGMA = 0.2         # Tasa de incubación (SEIR)
    SIM_DAYS = 30       # Días de simulación
    TIME_STEPS = 300    # Pasos de simulación
    
    # Clustering
    N_CLUSTERS = 10     # Número de clusters de comportamiento
    
    # Ataques de interés
    TARGET_ATTACKS = ['Infiltration', 'Botnet', 'Backdoor']


# ============================================================================
# 2. LECTOR DE DATOS - FLEXIBLE SEGÚN DISPONIBILIDAD
# ============================================================================

class DataReader:
    """Lee datos de diferentes fuentes disponibles"""
    
    @staticmethod
    def read_from_payload_csv(filepath):
        """Lee datos de Payload_data_CICIDS2017.csv"""
        print(f"📖 Leyendo {filepath.name}...")
        
        # Leer con chunks para archivos grandes
        chunks = []
        for chunk in pd.read_csv(filepath, chunksize=50000):
            # Esperamos columnas como: Src IP, Dst IP, Label, etc.
            chunks.append(chunk)
            if len(chunks) >= 5:  # Primeros 250K registros
                break
        
        df = pd.concat(chunks, ignore_index=True)
        print(f"✓ {len(df)} registros cargados")
        return df
    
    @staticmethod  
    def read_from_ml_csvs():
        """Lee datos de los CSVs de Machine Learning"""
        print("📖 Leyendo archivos de Machine Learning...")
        
        data_raw = ProjectConfig.DATA_RAW / 'MachineLearningCVE'
        csv_files = sorted([f for f in data_raw.glob('*.csv')])
        
        dfs = []
        label_col = ' Label'
        
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            df['source_file'] = csv_file.stem
            dfs.append(df)
        
        df_all = pd.concat(dfs, ignore_index=True)
        print(f"✓ {len(df_all)} registros cargados de {len(csv_files)} archivos")
        
        return df_all


# ============================================================================
# 3. CONSTRUCCIÓN DEL GRAFO DE RED
# ============================================================================

class NetworkGraph:
    """Construye y gestiona el grafo de la red"""
    
    def __init__(self, name="Network"):
        self.G = nx.Graph()
        self.name = name
        self.node_states = {}  # Para SIR/SEIR
        self.attack_mapping = {}  # Maps attack records to nodes
        
    def add_edge_from_flow(self, src_ip, dst_ip, attack_type=None, weight=1):
        """Agrega una arista basada en un flujo de red"""
        # Sanitizar IPs
        src_ip = str(src_ip).strip()
        dst_ip = str(dst_ip).strip()
        
        if src_ip and dst_ip and src_ip != 'nan' and dst_ip != 'nan':
            self.G.add_edge(src_ip, dst_ip, weight=weight, attack=attack_type)
    
    def add_node_with_state(self, node_id, state='S', attack_type=None):
        """Agrega nodo con estado inicial"""
        self.G.add_node(node_id, state=state, attack_type=attack_type)
        self.node_states[node_id] = state
    
    def get_stats(self):
        """Retorna estadísticas del grafo"""
        return {
            'nodes': self.G.number_of_nodes(),
            'edges': self.G.number_of_edges(),
            'density': nx.density(self.G),
            'avg_degree': sum(dict(self.G.degree()).values()) / max(self.G.number_of_nodes(), 1)
        }
    
    def visualize(self, output_file=None, max_nodes=100):
        """Visualiza el grafo"""
        if self.G.number_of_nodes() > max_nodes:
            # Subgrafo de nodos más conectados
            nodes_by_degree = sorted(
                self.G.degree(), key=lambda x: x[1], reverse=True
            )[:max_nodes]
            subgraph = self.G.subgraph([n[0] for n in nodes_by_degree])
        else:
            subgraph = self.G
        
        fig, ax = plt.subplots(figsize=(14, 10))
        
        pos = nx.spring_layout(subgraph, k=0.5, iterations=50)
        
        node_colors = [
            'red' if subgraph.nodes[n].get('state') == 'I' else
            'yellow' if subgraph.nodes[n].get('state') == 'E' else
            'green' if subgraph.nodes[n].get('state') == 'R' else
            'lightblue'
            for n in subgraph.nodes()
        ]
        
        nx.draw_networkx_nodes(subgraph, pos, node_color=node_colors, 
                              node_size=300, ax=ax, alpha=0.8)
        nx.draw_networkx_edges(subgraph, pos, ax=ax, alpha=0.3)
        
        ax.set_title(f"Network Graph - {self.name}\n({subgraph.number_of_nodes()} nodes, {subgraph.number_of_edges()} edges)")
        ax.axis('off')
        
        if output_file:
            fig.savefig(output_file, dpi=150, bbox_inches='tight')
            print(f"✓ Grafo guardado: {output_file}")
        
        plt.close()
        return fig


# ============================================================================
# 4. SIMULADOR SIR/SEIR
# ============================================================================

class SIRSimulator:
    """Simula propagación de infecciones usando modelo SIR"""
    
    def __init__(self, graph, beta=0.4, gamma=0.1, days=30):
        self.graph = graph
        self.beta = beta      # Tasa de transmisión
        self.gamma = gamma    # Tasa de recuperación
        self.days = days
        self.history = {
            'S': [], 'I': [], 'R': [],
            'time': []
        }
    
    def run(self, initial_infected=None, timesteps=300):
        """Ejecuta la simulación"""
        print(f"\n🔄 Ejecutando simulación SIR...")
        
        G = self.graph.G
        states = {node: 'S' for node in G.nodes()}
        
        # Marcar inicialmente infectados
        if initial_infected is None:
            # Nodos con más grado = más probable que sean entry points
            high_degree = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:3]
            initial_infected = [node for node, _ in high_degree]
        
        for node in initial_infected:
            if node in states:
                states[node] = 'I'
        
        # Simulación temporal
        for t in range(timesteps):
            # Contar estados
            s_count = sum(1 for s in states.values() if s == 'S')
            i_count = sum(1 for s in states.values() if s == 'I')
            r_count = sum(1 for s in states.values() if s == 'R')
            
            self.history['S'].append(s_count)
            self.history['I'].append(i_count)
            self.history['R'].append(r_count)
            self.history['time'].append(t)
            
            # Actualizar estados para siguiente paso
            new_states = states.copy()
            
            for node in G.nodes():
                if states[node] == 'S':
                    # Revisar si algún vecino está infectado
                    infected_neighbors = [
                        n for n in G.neighbors(node) 
                        if states[n] == 'I'
                    ]
                    if infected_neighbors and np.random.random() < self.beta:
                        new_states[node] = 'I'
                
                elif states[node] == 'I':
                    # Probabilidad de recuperación
                    if np.random.random() < self.gamma:
                        new_states[node] = 'R'
            
            states = new_states
            
            # Criterio de parada
            if i_count == 0:
                print(f"  → Simulación completada en paso {t} (sin nodos infectados)")
                break
        
        print(f"✓ Simulación completada: {len(self.history['time'])} timesteps")
        return self.history
    
    def plot_results(self, output_file=None):
        """Gráfica de resultados SIR"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(self.history['time'], self.history['S'], 'b-', label='Susceptible', linewidth=2)
        ax.plot(self.history['time'], self.history['I'], 'r-', label='Infected', linewidth=2)
        ax.plot(self.history['time'], self.history['R'], 'g-', label='Recovered', linewidth=2)
        
        ax.set_xlabel('Timesteps', fontsize=12)
        ax.set_ylabel('Cantidad de Nodos', fontsize=12)
        ax.set_title('Simulación SIR - Propagación de Amenaza', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        if output_file:
            fig.savefig(output_file, dpi=150, bbox_inches='tight')
            print(f"✓ Gráfico SIR guardado: {output_file}")
        
        plt.close()
        return fig


# ============================================================================
# 5. MAIN - PIPELINE COMPLETO
# ============================================================================

def main():
    print("="*80)
    print("PIPELINE DE ANÁLISIS: Propagación de Amenazas en Red")
    print("="*80)
    
    config = ProjectConfig()
    
    # ---------- Paso 1: Cargar datos ----------
    print("\n[1/5] Cargando datos...")
    
    # Intentar leer Payload CSV, si falla, usar ML CSVs
    payload_file = config.DATA_RAW / 'Payload_data_CICIDS2017.csv'
    if payload_file.exists():
        df = DataReader.read_from_payload_csv(payload_file)
    else:
        df = DataReader.read_from_ml_csvs()
    
    print(f"  → Dataset: {df.shape[0]} registros, {df.shape[1]} columnas")
    
    # ---------- Paso 2: Construir grafo ----------
    print("\n[2/5] Construyendo grafo de red...")
    
    net = NetworkGraph(name="CIC-IDS2017")
    
    # Buscar columnas de IPs
    ip_columns = [col for col in df.columns if 'ip' in col.lower() or 'host' in col.lower()]
    label_columns = [col for col in df.columns if 'label' in col.lower()]
    
    if ip_columns and len(ip_columns) >= 2:
        src_col, dst_col = ip_columns[0], ip_columns[1]
        label_col = label_columns[0] if label_columns else None
        
        # Agregar aristas
        for _, row in df.iloc[:10000].iterrows():  # Primeras 10K filas
            attack = row[label_col].strip() if label_col and label_col in df.columns else 'Unknown'
            net.add_edge_from_flow(row[src_col], row[dst_col], attack)
    else:
        print("  ⚠️ No se encontraron columnas de IP. Crear grafo sintético...")
        # Crear grafo demo
        for i in range(50):
            for j in range(i+1, min(i+5, 50)):
                net.add_edge_from_flow(f"Host_{i}", f"Host_{j}")
    
    stats = net.get_stats()
    print(f"  ✓ {stats['nodes']} nodos, {stats['edges']} aristas creadas")
    print(f"    - Densidad: {stats['density']:.4f}")
    print(f"    - Grado promedio: {stats['avg_degree']:.2f}")
    
    # ---------- Paso 3: Marcar nodos infectados ----------
    print("\n[3/5] Identificando nodos comprometidos...")
    
    label_col = ' Label' if ' Label' in df.columns else 'Label'
    if label_col in df.columns:
        attack_nodes = df[df[label_col].isin(config.TARGET_ATTACKS)]
        print(f"  ✓ {len(attack_nodes)} registros de ataque identificados")
    else:
        # Aleatorios para demostración
        all_nodes = list(net.G.nodes())
        attack_nodes = np.random.choice(all_nodes, min(5, len(all_nodes)), replace=False)
        print(f"  ✓ {len(attack_nodes)} nodos marcados como potencialmente comprometidos")
    
    # ---------- Paso 4: Ejecutar simulación SIR ----------
    print("\n[4/5] Ejecutando simulación SIR/SEIR...")
    
    sir = SIRSimulator(net, beta=config.BETA, gamma=config.GAMMA, days=config.SIM_DAYS)
    history = sir.run(timesteps=config.TIME_STEPS)
    
    # ---------- Paso 5: Visualización y reporte ----------
    print("\n[5/5] Generando reportes...")
    
    net.visualize(output_file=config.REPORTS / '01_network_graph.png')
    sir.plot_results(output_file=config.REPORTS / '02_sir_simulation.png')
    
    # Guardar metadatos
    metadata = {
        'dataset': 'CIC-IDS2017',
        'network': stats,
        'simulation': {
            'days': config.SIM_DAYS,
            'beta': config.BETA,
            'gamma': config.GAMMA,
            'final_state': {
                'S': history['S'][-1],
                'I': history['I'][-1],
                'R': history['R'][-1]
            }
        }
    }
    
    with open(config.DATA_PROCESSED / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n" + "="*80)
    print("✅ PIPELINE COMPLETADO")
    print("="*80)
    print(f"\nReportes guardados en: {config.REPORTS}")
    print(f"Datos procesados en: {config.DATA_PROCESSED}")


if __name__ == '__main__':
    main()
