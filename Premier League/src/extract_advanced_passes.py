import json
import os

def extract_advanced_passes():
    json_path = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League\data\raw\scraped_data\whoscored_everton_burnley_full_events.json"
    
    if not os.path.exists(json_path):
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    events = data.get('events', [])
    player_dict = data.get('playerIdNameDictionary', {})
    
    everton_passes = []
    for i in range(len(events)):
        ev = events[i]
        # Filter for Pass (ID 1) by Everton (ID 31)
        if ev.get('type', {}).get('value') == 1 and ev.get('teamId') == 31:
            p_id = str(ev.get('playerId'))
            outcome = ev.get('outcomeType', {}).get('displayName')
            
            # Try to find receiver
            receiver = "Unknown"
            if outcome == "Successful" and i + 1 < len(events):
                next_ev = events[i+1]
                if next_ev.get('teamId') == 31:
                    r_id = str(next_ev.get('playerId'))
                    receiver = player_dict.get(r_id, "Unknown")
            
            everton_passes.append({
                "x": ev.get('x'),
                "y": ev.get('y'),
                "endX": ev.get('endX'),
                "endY": ev.get('endY'),
                "player": player_dict.get(p_id, "Unknown"),
                "receiver": receiver,
                "outcome": outcome,
                "minute": ev.get('minute'),
                "second": ev.get('second')
            })
            
    output_path = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League\data\raw\scraped_data\everton_passes_advanced.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(everton_passes, f, indent=4)
    print(f"Extracted {len(everton_passes)} advanced passes.")

if __name__ == "__main__":
    extract_advanced_passes()
