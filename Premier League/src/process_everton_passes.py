import json
import os

def process_passes():
    json_path = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League\data\raw\scraped_data\whoscored_everton_burnley_full_events.json"
    output_path = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League\data\raw\scraped_data\everton_passes_processed.json"
    
    if not os.path.exists(json_path):
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    events = data.get('events', [])
    player_dict = data.get('playerIdNameDictionary', {})
    
    everton_passes = []
    for ev in events:
        # Filter for Pass (ID 1) by Everton (ID 31)
        if ev.get('type', {}).get('value') == 1 and ev.get('teamId') == 31:
            p_id = str(ev.get('playerId'))
            everton_passes.append({
                "x": ev.get('x'),
                "y": ev.get('y'),
                "endX": ev.get('endX'),
                "endY": ev.get('endY'),
                "player": player_dict.get(p_id, "Unknown"),
                "outcome": ev.get('outcomeType', {}).get('displayName'),
                "minute": ev.get('minute'),
                "second": ev.get('second')
            })
            
    print(f"Extracted {len(everton_passes)} passes for Everton.")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(everton_passes, f, indent=4)
    print(f"Processed data saved to {output_path}")

if __name__ == "__main__":
    process_passes()
