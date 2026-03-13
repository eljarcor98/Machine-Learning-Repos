import json
import re
import os
import argparse

def extract_from_local_html(html_path, output_path):
    if not os.path.exists(html_path):
        print(f"Error: File not found at {html_path}")
        return

    print(f"Reading local HTML: {os.path.basename(html_path)}")
    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        start_marker = "matchCentreData:"
        idx = content.find(start_marker)
            
        if idx != -1:
            start_json = content.find('{', idx)
            if start_json != -1:
                brace_count = 0
                end_json = -1
                for i in range(start_json, len(content)):
                    if content[i] == '{':
                        brace_count += 1
                    elif content[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_json = i + 1
                            break
                
                if end_json != -1:
                    json_str = content[start_json:end_json]
                    try:
                        data = json.loads(json_str)
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        with open(output_path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=4)
                        print(f"SUCCESS: Extracted {len(data.get('events', []))} events.")
                        print(f"File saved to: {output_path}")
                    except json.JSONDecodeError as e:
                        print(f"JSON Parse Error: {e}")
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(json_str)
                        print("Saved raw string despite parse error for manual debugging.")
                else:
                    print("Error: Could not find matching closing brace.")
            else:
                print("Error: Could not find start of JSON object '{'.")
        else:
            print("Error: Could not find 'matchCentreData' marker.")
            
    except Exception as e:
        print(f"Processing error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract matchCentreData from WhoScored local HTML")
    parser.add_argument("input", help="Path to the local HTML file")
    parser.add_argument("output", help="Path to save the extracted JSON")
    args = parser.parse_args()
    
    extract_from_local_html(args.input, args.output)
