import json
import os

def inject_advanced_data():
    json_path = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League\data\raw\scraped_data\everton_passes_advanced.json"
    html_path = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League\reports\match_viewer_everton_burnley.html"
    
    if not os.path.exists(json_path) or not os.path.exists(html_path):
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        passes_data = json.load(f)
    
    passes_js = "const PASSES = " + json.dumps(passes_data, indent=6) + ";"
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Rebuild the PASSES block
    start_tag = "const PASSES ="
    idx_start = content_start = html_content.find(start_tag)
    
    # We replaced the block before, so it might be large. 
    # Let's find the next block: // ── DOM refs ──
    next_block = "// ── DOM refs ──"
    idx_next = html_content.find(next_block, idx_start)
    
    if idx_start != -1 and idx_next != -1:
        header = html_content[:idx_start]
        footer = html_content[idx_next:]
        new_content = header + passes_js + "\n\n    " + footer
        
        # Also clean up the popup logic if needed, but let's just update the pass rendering
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Advanced PASSES injected with receiver data.")
    else:
        print("Markers not found.")

if __name__ == "__main__":
    inject_advanced_data()
