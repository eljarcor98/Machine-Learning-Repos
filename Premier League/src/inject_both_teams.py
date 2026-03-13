import json
import os
import argparse

def inject_both_teams_data(json_path, html_path):
    if not os.path.exists(json_path) or not os.path.exists(html_path):
        print(f"Error: Missing files. JSON: {os.path.exists(json_path)}, HTML: {os.path.exists(html_path)}")
        return

    print(f"Injecting data from {os.path.basename(json_path)} into {os.path.basename(html_path)}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    passes_js = "const PASSES = " + json.dumps(data['passes'], indent=6) + ";"
    players_js = "const PLAYERS = " + json.dumps(data['players'], indent=6) + ";"
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace PASSES block
    start_passes = "const PASSES ="
    idx_passes_start = content.find(start_passes)
    idx_passes_next = content.find("// ── DOM refs ──", idx_passes_start)
    
    # Replace PLAYERS block
    start_players = "const PLAYERS = ["
    idx_players_start = content.find(start_players)
    idx_players_end = content.find("];", idx_players_start) + 2
    
    if idx_passes_start != -1 and idx_passes_next != -1 and idx_players_start != -1:
        # Rebuild HTML content
        header_temp = content[:idx_players_start]
        footer_temp = content[idx_players_end:]
        content_no_players = header_temp + players_js + footer_temp
        
        idx_passes_start = content_no_players.find(start_passes)
        idx_passes_next = content_no_players.find("// ── DOM refs ──", idx_passes_start)
        
        header = content_no_players[:idx_passes_start]
        footer = content_no_players[idx_passes_next:]
        
        final_content = header + passes_js + "\n\n    " + footer
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        print("SUCCESS: Tactical data injected.")
    else:
        print(f"Error: Markers not found. Check if the HTML template has 'const PASSES =' and 'const PLAYERS ='.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject tactical data into WhoScored match viewer")
    parser.add_argument("json", help="Path to the processed tactical JSON")
    parser.add_argument("html", help="Path to the target match viewer HTML")
    args = parser.parse_args()
    
    inject_both_teams_data(args.json, args.html)
