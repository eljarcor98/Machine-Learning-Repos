import json
import os
import argparse

def extract_all_teams_passes(json_path, output_path):
    if not os.path.exists(json_path):
        print(f"Error: File not found at {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    events = data.get('events', [])
    player_dict = data.get('playerIdNameDictionary', {})
    
    all_passes = []
    for i in range(len(events)):
        ev = events[i]
        if ev.get('type', {}).get('value') == 1:
            team_id = ev.get('teamId')
            p_id = str(ev.get('playerId'))
            outcome = ev.get('outcomeType', {}).get('displayName')
            
            receiver = "Unknown"
            if outcome == "Successful" and i + 1 < len(events):
                next_ev = events[i+1]
                if next_ev.get('teamId') == team_id:
                    r_id = str(next_ev.get('playerId'))
                    receiver = player_dict.get(r_id, "Unknown")
            
            all_passes.append({
                "x": ev.get('x'),
                "y": ev.get('y'),
                "endX": ev.get('endX'),
                "endY": ev.get('endY'),
                "player": player_dict.get(p_id, "Unknown"),
                "receiver": receiver,
                "teamId": team_id,
                "outcome": outcome,
                "minute": ev.get('minute'),
                "second": ev.get('second')
            })
            
    players_data = []
    seen_players = set()
    
    for ev in events:
        p_id_val = ev.get('playerId')
        if p_id_val and p_id_val not in seen_players:
            p_id = str(p_id_val)
            players_data.append({
                "id": p_id,
                "name": player_dict.get(p_id, "Unknown"),
                "teamId": ev.get('teamId'),
                "x": ev.get('x'),
                "y": ev.get('y')
            })
            seen_players.add(p_id_val)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "passes": all_passes,
            "players": players_data
        }, f, indent=4)
        
    print(f"Extracted {len(all_passes)} passes and {len(players_data)} players to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process WhoScored match events for tactical visualization")
    parser.add_argument("input", help="Path to the full events JSON")
    parser.add_argument("output", help="Path to save the processed tactical JSON")
    args = parser.parse_args()
    
    extract_all_teams_passes(args.input, args.output)
