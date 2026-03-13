import json
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def generate_creation_network():
    base_dir = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League"
    json_path = os.path.join(base_dir, 'data', 'raw', 'scraped_data', 'whoscored_everton_burnley.json')
    output_dir = os.path.join(base_dir, 'reports', 'figures')
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(json_path):
        print(f"Error: {json_path} no encontrado.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    html_content = data.get('html', '')
    markdown_content = data.get('markdown', '')

    # 1. Extraer Coordenadas de Jugadores del Everton (Team 31)
    # Buscamos la sección "pitch-field" del equipo local
    pitch_field_pattern = re.compile(r'<div class="pitch-field" data-team-id="31".*?>(.*?)</div>\s*<div class="pitch-field"', re.DOTALL)
    pitch_match = pitch_field_pattern.search(html_content)
    
    player_data = {}
    if pitch_match:
        pitch_html = pitch_match.group(1)
        # Regex para capturar data-player-id, left, bottom y title
        # <div class="player" data-player-id="110189" ... style="left: 0%; bottom: 45.4545%;"><div ... title="Jordan Pickford">
        p_regex = re.compile(r'data-player-id="(\d+)".*?style="left:\s*([\d.]+)%;\s*bottom:\s*([\d.]+)%;".*?title="(.*?)"', re.DOTALL)
        matches = p_regex.findall(pitch_html)
        
        for p_id, x, y, name in matches:
            player_data[p_id] = {
                'name': name,
                'x': float(x),
                'y': float(y),
                'key_passes': 0,
                'is_starter': True
            }
            print(f"Parsed: {name} (ID: {p_id}) at ({x}, {y})")

    # 2. Extraer Key Passes del Markdown
    # Buscamos específicamente la sección de "Key passes" en los detalles
    # Las secciones de detalles suelen tener este formato: data-detail-for="passSuccess" ... Key passes
    kp_section_regex = re.compile(r'data-detail-for="passSuccess".*?Key passes.*?Close x', re.DOTALL)
    kp_section = kp_section_regex.search(markdown_content)
    
    if kp_section:
        # En esta sección, los jugadores se listan con su valor
        # Ejemplo: 1...James Garner...7.6 (Nota: en el markdown el valor parece ser el rating o touches en el top 5, 
        # pero para propósitos de visualización buscaremos el valor numérico al final de la línea del jugador)
        p_row_regex = re.compile(r'(\d+)!\[\].*?([a-zA-Z\s\'-]+)\(.*?\)Everton([\d.]+)')
        rows = p_row_regex.findall(kp_section.group())
        for idx, name, val in rows:
            name_clean = name.strip()
            # Asignar al jugador correspondiente
            for p_id, p_info in player_data.items():
                if name_clean in p_info['name']:
                    p_info['key_passes'] = float(val)
                    print(f"Key Passes for {name_clean}: {val}")

    # 3. Datos de Asistencias (IDs basados en el parsing real)
    assists = []
    # Identificar IDs dinámicamente
    def find_id(name_part):
        return next((id for id, info in player_data.items() if name_part in info['name']), None)

    garner_id = find_id("Garner")
    tarkowski_id = find_id("Tarkowski")
    ndiaye_id = find_id("Ndiaye")
    dhall_id = find_id("Dewsbury-Hall")

    if garner_id and tarkowski_id:
        assists.append((garner_id, tarkowski_id, 'Free-kick Assist'))
    if ndiaye_id and dhall_id:
        assists.append((ndiaye_id, dhall_id, 'Through Ball Assist'))

    # 4. Dibujar Campo y Red
    plt.ioff() # Evitar que se abra ventana
    fig, ax = plt.subplots(figsize=(14, 9), facecolor='#0e1117')
    ax.set_facecolor('#0e1117')

    # Campo de fútbol estilizado
    # Bordes (0-100 en el sistema de Whoscored)
    field = patches.Rectangle((0, 0), 100, 100, linewidth=2, edgecolor='#3d444d', facecolor='none', zorder=1)
    ax.add_patch(field)
    
    # Línea media y círculo
    plt.axvline(x=50, color='#3d444d', linestyle='-', alpha=0.5, zorder=1)
    center_circle = patches.Circle((50, 50), 9.15, linewidth=1, edgecolor='#3d444d', facecolor='none', alpha=0.5, zorder=1)
    ax.add_patch(center_circle)
    
    # Áreas
    # Izquierda
    ax.add_patch(patches.Rectangle((0, 21.1), 16.5, 57.8, linewidth=1, edgecolor='#3d444d', facecolor='none', alpha=0.5, zorder=1))
    ax.add_patch(patches.Rectangle((0, 36.8), 5.5, 26.4, linewidth=1, edgecolor='#3d444d', facecolor='none', alpha=0.5, zorder=1))
    # Derecha
    ax.add_patch(patches.Rectangle((83.5, 21.1), 16.5, 57.8, linewidth=1, edgecolor='#3d444d', facecolor='none', alpha=0.5, zorder=1))
    ax.add_patch(patches.Rectangle((94.5, 36.8), 5.5, 26.4, linewidth=1, edgecolor='#3d444d', facecolor='none', alpha=0.5, zorder=1))

    # Dibujar Conectividad (Asistencias) primero para que queden debajo
    for start_id, end_id, label in assists:
        if start_id in player_data and end_id in player_data:
            start = player_data[start_id]
            end = player_data[end_id]
            # Flecha curva
            arrow = patches.FancyArrowPatch((start['x'], start['y']), (end['x'], end['y']),
                                           connectionstyle="arc3,rad=.2",
                                           arrowstyle='-|>', 
                                           color='#00ff88', 
                                           lw=2.5, 
                                           mutation_scale=20, 
                                           alpha=0.8,
                                           zorder=2)
            ax.add_patch(arrow)
            # Etiqueta
            mid_x = (start['x'] + end['x']) / 2 + 2
            mid_y = (start['y'] + end['y']) / 2 + 2
            ax.text(mid_x, mid_y, label, color='#00ff88', fontsize=9, fontweight='bold',
                    bbox=dict(facecolor='#0e1117', alpha=0.7, edgecolor='none', pad=1))

    # Dibujar Jugadores
    for p_id, p in player_data.items():
        # Escalar tamaño: mínimo 400, máximo 1200
        # Usamos key_passes como factor. Si es 0, usamos base.
        base_size = 500
        size = base_size + (p['key_passes'] * 200)
        
        # Sombra/Brillo exterior
        ax.scatter(p['x'], p['y'], s=size*1.3, color='#00aaff', alpha=0.1, zorder=3)
        # Jugador
        ax.scatter(p['x'], p['y'], s=size, color='#0044cc', edgecolors='white', linewidth=1.5, zorder=4)
        
        # Etiqueta de nombre
        last_name = p['name'].split()[-1]
        ax.text(p['x'], p['y'] + 4.5, last_name, color='white', ha='center', 
                fontsize=10, fontweight='bold', zorder=5,
                path_effects=[]) # Sin efectos para limpiar
        
        # Burbuja de Key Passes si tiene
        if p['key_passes'] > 0:
            ax.text(p['x'], p['y'] - 5.5, f"KP: {int(p['key_passes'])}", 
                    color='#00ff88', ha='center', fontsize=9, fontweight='bold', zorder=5)

    # Títulos y Leyenda
    plt.title('EVERTON CREATION NETWORK\nStrategic Player Positioning & Goal Creation', 
              color='white', pad=30, fontsize=18, fontweight='bold')
    plt.text(50, -5, 'Everton 2-0 Burnley | Premier League | Mar-2026', 
             color='#888888', ha='center', fontsize=12)
    
    # Leyenda personalizada
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='none', label='Player Position',
               markerfacecolor='#0044cc', markeredgecolor='white', markersize=10),
        Line2D([0], [0], color='#00ff88', lw=2, label='Goal Assist', marker='>', markersize=5),
        Line2D([0], [0], marker='o', color='none', label='Circle Size = Key Passes',
               markerfacecolor='none', markeredgecolor='#00aaff', markersize=12)
    ]
    ax.legend(handles=legend_elements, loc='upper right', facecolor='#1a1a1a', 
              edgecolor='#3d444d', labelcolor='white', fontsize=10)

    plt.xlim(-5, 105)
    plt.ylim(-10, 110)
    plt.axis('off')

    output_path = os.path.join(output_dir, 'creation_network_everton.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#0e1117')
    plt.close()

    print(f"Success: Visual generated at {output_path}")

if __name__ == "__main__":
    generate_creation_network()
