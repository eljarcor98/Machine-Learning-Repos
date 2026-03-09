from firecrawl import Firecrawl
import json
import os

def perform_scrape(api_key, url, filename):
    """
    Realiza un scrape usando Firecrawl SDK v2 y guarda el resultado como JSON.
    """
    app = Firecrawl(api_key=api_key)
    print(f"Iniciando scrape de: {url}...")
    
    try:
        # Ejecutar scrape
        scrape_result = app.scrape(url, formats=['markdown'])
        
        if scrape_result:
            # El resultado es un objeto Pydantic (Document). 
            # Lo convertimos a diccionario para poder guardarlo como JSON.
            data_dict = scrape_result.model_dump()
            
            output_dir = os.path.join('data', 'raw', 'scraped_data')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{filename}.json")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, indent=4, ensure_ascii=False)
            
            print("Conexion exitosa con Firecrawl.")
            print(f"Resultado guardado en: {output_path}")
            print(f"Titulo detectado: {data_dict.get('metadata', {}).get('title')}")
            return data_dict
            
    except Exception as e:
        print(f"Error en el proceso de Firecrawl: {e}")
        return None

if __name__ == "__main__":
    # API Key del usuario
    API_KEY = 'fc-a98a997aa2bc43c1bd721f7c5b9edbdd'
    
    # URL de prueba (Noticias de la Premier League en BBC)
    test_url = 'https://www.bbc.com/sport/football/premier-league'
    
    print("--- FIRECRAWL v2 SCRAPER ---")
    perform_scrape(API_KEY, test_url, 'bbc_pl_news_test')
