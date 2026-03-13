import json
import re
import os

def count_data():
    parsed_path = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League\data\raw\scraped_data\whoscored_everton_burnley_parsed.json"
    bbc_path = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League\data\raw\scraped_data\bbc_pl_news_test.json"
    
    results = {}
    
    if os.path.exists(parsed_path):
        with open(parsed_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            results['match'] = data.get('match', 'N/A')
            results['timeline_events'] = len(data.get('timeline', []))
            home_subs = len(data.get('teams', {}).get('home', {}).get('substitutions', []))
            away_subs = len(data.get('teams', {}).get('away', {}).get('substitutions', []))
            results['total_substitutions'] = home_subs + away_subs
            results['goals'] = len(data.get('teams', {}).get('home', {}).get('goalscorers', [])) + len(data.get('teams', {}).get('away', {}).get('goalscorers', []))
            
    if os.path.exists(bbc_path):
        with open(bbc_path, 'r', encoding='utf-8') as f:
            bbc_data = json.load(f)
            md = bbc_data.get('markdown', '')
            # Count articles (matches starting with - [Title](URL))
            articles = re.findall(r'^- \[.*?\]\(.*?\)', md, re.MULTILINE)
            results['bbc_articles'] = len(articles)
            
            # Count videos (matches with Video, duration)
            videos = re.findall(r'Video, \d{2}:\d{2}:\d{2}', md)
            results['bbc_videos'] = len(videos)

    print(json.dumps(results, indent=4))

if __name__ == "__main__":
    count_data()
