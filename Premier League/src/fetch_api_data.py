import requests
import json
import os

def fetch_premier_league_matches(api_key):
    uri = 'https://api.football-data.org/v4/competitions/PL/matches'
    headers = { 'X-Auth-Token': api_key }

    print(f"Conectando a {uri}...")
    try:
        response = requests.get(uri, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Mostrar el primer partido como prueba
        if data['matches']:
            first_match = data['matches'][0]
            print("\nConexion exitosa!")
            print(f"Primer partido encontrado: {first_match['homeTeam']['name']} vs {first_match['awayTeam']['name']}")
            print(f"Fecha: {first_match['utcDate']}")
            
            # Guardar una muestra en data/raw para referencia
            output_json = os.path.join('data', 'raw', 'api_sample_matches.json')
            output_csv = os.path.join('data', 'raw', 'api_sample_matches.csv')
            os.makedirs(os.path.dirname(output_json), exist_ok=True)
            
            # Guardar JSON
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            # Guardar CSV (Aplanado)
            import pandas as pd
            df = pd.json_normalize(data['matches'])
            df.to_csv(output_csv, index=False, encoding='utf-8')
            
            print(f"\nDatos guardados en:\n- JSON: {output_json}\n- CSV: {output_csv}")
        else:
            print("No se encontraron partidos.")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la conexión: {e}")

if __name__ == "__main__":
    API_KEY = '184592c51a7749c2919607126c956610'
    fetch_premier_league_matches(API_KEY)
