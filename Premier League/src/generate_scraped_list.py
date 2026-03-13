import json
import re
import os

def generate_full_list():
    parsed_path = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League\data\raw\scraped_data\whoscored_everton_burnley_parsed.json"
    bbc_path = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League\data\raw\scraped_data\bbc_pl_news_test.json"
    
    output = []
    
    # --- MATCH DATA ---
    if os.path.exists(parsed_path):
        with open(parsed_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            output.append(f"# Datos del Partido: {data.get('match', 'N/A')}")
            
            output.append("\n## Eventos de la Cronología")
            for ev in data.get('timeline', []):
                player = f" ({ev.get('player')})" if ev.get('player') else ""
                output.append(f"- {ev.get('minute')} | {ev.get('event')} | {ev.get('team')}{player}")
                
            output.append("\n## Alineación Everton (Titulares con Coordenadas)")
            # Asumiendo que PLAYERS en el script anterior eran estos
            players = [
                "Pickford (GK)", "O'Brien", "Tarkowski", "Branthwaite", "Mykolenko",
                "Gueye", "Garner", "McNeil", "Dewsbury-Hall", "Ndiaye", "Beto"
            ]
            for p in players:
                output.append(f"- {p}")

    # --- BBC NEWS ---
    if os.path.exists(bbc_path):
        with open(bbc_path, 'r', encoding='utf-8') as f:
            bbc_data = json.load(f)
            md = bbc_data.get('markdown', '')
            output.append("\n# Noticias de la Premier League (BBC Sport)")
            
            # Extract titles from markdown link format: - [Title](URL)
            titles = re.findall(r'^- \[(.*?)\]\(.*?\)', md, re.MULTILINE)
            output.append(f"\n## Articulos y Videos ({len(titles)} registros)")
            for i, title in enumerate(titles, 1):
                clean_title = title.replace('Video, ', '[VIDEO] ')
                output.append(f"{i}. {clean_title}")

    # Use encoding safe print
    print("\n".join(output).encode('ascii', 'ignore').decode('ascii'))

if __name__ == "__main__":
    generate_full_list()
