import requests
import os

def download_season(season_code, output_dir):
    url = f"https://www.football-data.co.uk/mmz4281/{season_code}/E0.csv"
    output_path = os.path.join(output_dir, f"pl_{season_code}.csv")
    
    print(f"Downloading {season_code} from {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"Saved to {output_path}")
    except Exception as e:
        print(f"Error downloading {season_code}: {e}")

if __name__ == "__main__":
    base_dir = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League\data\raw"
    os.makedirs(base_dir, exist_ok=True)
    
    # Test with 2324
    download_season("2324", base_dir)
    # Also 2425 if possible
    download_season("2425", base_dir)
