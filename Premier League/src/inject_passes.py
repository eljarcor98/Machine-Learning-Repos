import json
import os

def inject_passes():
    json_path = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League\data\raw\scraped_data\everton_passes_processed.json"
    html_path = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League\reports\match_viewer_everton_burnley.html"
    
    if not os.path.exists(json_path) or not os.path.exists(html_path):
        print("Required files not found.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        passes_data = json.load(f)
        
    passes_js = json.dumps(passes_data, indent=6)
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    marker = "/* DATA_INJECTION_POINT */"
    if marker in html_content:
        new_content = html_content.replace(marker, passes_js)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Successfully injected {len(passes_data)} passes into HTML.")
    else:
        print("Marker not found in HTML.")

if __name__ == "__main__":
    inject_passes()
