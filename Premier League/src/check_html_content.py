import os

def check_file_content():
    html_path = r"C:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League\data\raw\scraped_data\Everton 2-0 Burnley - Premier League 2025_2026 Live.html"
    
    if not os.path.exists(html_path):
        print("File not found.")
        return

    search_terms = ["matchCentreData", "playerId", "events", "matchId", "teamId"]
    found = {term: False for term in search_terms}
    
    print(f"Checking for terms in 1.45 MB file: {html_path}")
    
    with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
        # Read in 100KB chunks to handle potentially long lines
        while True:
            chunk = f.read(1024 * 100)
            if not chunk:
                break
            for term in search_terms:
                if term in chunk:
                    found[term] = True
                    
    print("Search results:")
    for term, is_found in found.items():
        print(f"- {term}: {'Found' if is_found else 'Not Found'}")

if __name__ == "__main__":
    check_file_content()
