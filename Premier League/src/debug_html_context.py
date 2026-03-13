import os

def debug_context():
    html_path = r"C:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League\data\raw\scraped_data\Everton 2-0 Burnley - Premier League 2025_2026 Live.html"
    
    if not os.path.exists(html_path):
        return

    term = "matchCentreData"
    with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    idx = content.find(term)
    if idx != -1:
        print(f"Found '{term}' at index {idx}")
        # Print 100 characters before and 200 after
        start = max(0, idx - 100)
        end = min(len(content), idx + 300)
        print("Context:")
        print(content[start:end])
    else:
        print(f"'{term}' NOT found in full read.")

if __name__ == "__main__":
    debug_context()
