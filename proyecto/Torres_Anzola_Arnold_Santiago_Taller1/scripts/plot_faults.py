import geopandas as gpd
import matplotlib.pyplot as plt
import os

# Rutas
geojson_path = r'data/Atlas_Geol%C3%B3gico_de_Colombia_2020%3A_Fallas_Geol%C3%B3gicas.geojson'
world_json_path = r'data/world.geojson'
output_path = r'documentacion/visualizaciones/mapa_fallas_colombia.png'
os.makedirs(os.path.dirname(output_path), exist_ok=True)

def plot_faults():
    print(f"Leyendo GeoJSON de fallas: {geojson_path}...")
    try:
        # Cargamos el GeoJSON de fallas
        gdf_fallas = gpd.read_file(geojson_path)
        
        # Cargamos el GeoJSON del mundo y filtramos por Colombia
        print(f"Leyendo bordes de Colombia: {world_json_path}...")
        world = gpd.read_file(world_json_path)
        
        # Intentamos filtrar por nombre o código ISO
        # Columnas disponibles: ['name', 'ISO3166-1-Alpha-3', 'ISO3166-1-Alpha-2', 'geometry']
        colombia = world[(world['name'] == 'Colombia') | (world['ISO3166-1-Alpha-3'] == 'COL')]
        
        if colombia.empty:
             print("Advertencia: No se encontró el croquis de Colombia en world.geojson. Se graficará sin fondo.")
        
        # Configuramos la figura
        fig, ax = plt.subplots(figsize=(10, 12))
        
        # 1. Graficamos el fondo de Colombia
        if not colombia.empty:
            colombia.plot(ax=ax, color='#eeeeee', edgecolor='#999999', linewidth=1.5)
            
        # 2. Graficamos las fallas
        # Usamos un color rojo brillante para las fallas para que resalten
        gdf_fallas.plot(ax=ax, color='red', linewidth=0.8, alpha=0.8, label='Fallas Geológicas')
        
        # Estética del mapa
        ax.set_title('Mapa de Fallas Geológicas de Colombia\n(Con contexto geográfico)', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Longitud', fontsize=12)
        ax.set_ylabel('Latitud', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.3)
        
        # Ajustar límites para centrarse en Colombia
        if not colombia.empty:
            bounds = colombia.total_bounds # [minx, miny, maxx, maxy]
            ax.set_xlim([bounds[0] - 1, bounds[2] + 1])
            ax.set_ylim([bounds[1] - 1, bounds[3] + 1])
        
        ax.set_facecolor('white')
        
        # Guardamos la imagen
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Mapa mejorado guardado exitosamente en: {output_path}")
        
    except Exception as e:
        print(f"Error al procesar los datos geográficos: {e}")

if __name__ == "__main__":
    plot_faults()
