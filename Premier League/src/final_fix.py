import json
import os

def final_fix():
    html_path = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League\reports\match_viewer_everton_burnley.html"
    json_path = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League\data\raw\scraped_data\everton_passes_processed.json"
    
    if not os.path.exists(html_path) or not os.path.exists(json_path):
        print("Files not found.")
        return

    # Original template parts (approximate)
    with open(json_path, 'r', encoding='utf-8') as f:
        passes_data = json.load(f)
    
    passes_js = "const PASSES = " + json.dumps(passes_data, indent=6) + ";"
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the start of the messed up PASSES block
    start_tag = "const PASSES = ["
    idx_start = content.find(start_tag)
    
    # Find the end of the JS script block where update(0) is called
    end_marker = "    update(0);"
    idx_end = content.find(end_marker)
    
    if idx_start != -1 and idx_end != -1:
        # We want to replace from idx_start to just before the next functional block
        # Let's find the 'const scrubber =' line which is the start of the next block
        next_block_start = "    // ── DOM refs ──"
        idx_next = content.find(next_block_start, idx_start)
        
        if idx_next != -1:
            header = content[:idx_start]
            footer = content[idx_next:]
            new_content = header + passes_js + "\n\n" + footer
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("HTML corrected by rebuilding the PASSES section.")
        else:
            print("Could not find next block start.")
    else:
        print(f"Could not find markers. Start: {idx_start}, End: {idx_end}")

if __name__ == "__main__":
    final_fix()
