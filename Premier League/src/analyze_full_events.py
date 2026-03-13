import json
import os

def analyze_json():
    json_path = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League\data\raw\scraped_data\whoscored_everton_burnley_full_events.json"
    
    if not os.path.exists(json_path):
        print("JSON not found.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Match ID: {data.get('matchId')}")
    print(f"Total Events: {len(data.get('events', []))}")
    
    # Analyze first 5 events
    events = data.get('events', [])
    for i in range(min(5, len(events))):
        ev = events[i]
        print(f"\nEvent {i}:")
        print(f"  Type: {ev.get('type', {}).get('displayName')} (ID: {ev.get('type', {}).get('value')})")
        print(f"  Team ID: {ev.get('teamId')}")
        print(f"  Coordinates: ({ev.get('x')}, {ev.get('y')}) -> ({ev.get('endX')}, {ev.get('endY')})")
        print(f"  Outcome: {ev.get('outcomeType', {}).get('displayName')}")
        
    # Check for team IDs
    teams = set(ev.get('teamId') for ev in events)
    print(f"\nTeam IDs in data: {teams}")

if __name__ == "__main__":
    analyze_json()
