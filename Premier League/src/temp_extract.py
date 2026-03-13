import json
import os

def extract_markdown():
    fpath = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League\data\raw\scraped_data\whoscored_everton_burnley.json"
    output_path = r"C:\Users\Arnold's\.gemini\antigravity\brain\8d957046-4ae8-44e6-acfb-12c0b82fca50\markdown_extract.txt"
    
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            html_full = data.get('html', '')
            # Buscar menciones a eventos o el script de chalkboard
            search_terms = ['matchCentreData', 'data-event-type="1"']
            for term in search_terms:
                idx = html_full.find(term)
                if idx != -1:
                    print(f"Found '{term}' at {idx}")
                    print(html_full[idx:idx+1000])
                else:
                    print(f"Term '{term}' not found.")
            
        print(f"Deep search completed in: {fpath}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_markdown()
