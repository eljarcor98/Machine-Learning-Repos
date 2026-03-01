import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os
import urllib.parse

# Configuración de rutas
DATA_DIR = 'data'
VIS_DIR = 'documentacion/visualizaciones'
RAW_DATA = os.path.join(DATA_DIR, 'earthquakes_raw.csv')
GEOJSON_FAULT_PATH = os.path.join(DATA_DIR, "Atlas_Geol%C3%B3gico_de_Colombia_2020%3A_Fallas_Geol%C3%B3gicas.geojson")
WORLD_GEOJSON = os.path.join(DATA_DIR, 'world.geojson')
OUTPUT_IMAGE = os.path.join(VIS_DIR, 'mapa_timeline_sismico.png')

def generate_seismic_timeline_map():
    print("Iniciando generación de mapa con timeline...")
    os.makedirs(VIS_DIR, exist_ok=True)

    try:
        # 1. Cargar Datos
        df = pd.read_csv(RAW_DATA)
        df['time'] = pd.to_datetime(df['time'])
        df['year'] = df['time'].dt.year
        
        gdf_fallas = gpd.read_file(GEOJSON_FAULT_PATH)
        world = gpd.read_file(WORLD_GEOJSON)
        colombia = world[(world['name'] == 'Colombia') | (world['ISO3166-1-Alpha-3'] == 'COL')]

        # 2. Configurar la Figura con GridSpec
        fig = plt.figure(figsize=(12, 14), facecolor='#f8f9fa')
        gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1], hspace=0.15)
        
        # --- PANEL SUPERIOR: MAPA DE FALLAS ---
        ax0 = fig.add_subplot(gs[0])
        
        # Fondo Regional (Países de la zona)
        if not world.empty:
            # Dibujamos todos los países para dar contexto regional
            world.plot(ax=ax0, color='#e9ecef', edgecolor='#adb5bd', linewidth=0.8, zorder=1)
            
            # Ajustamos los límites basados en la extensión de los sismos
            lon_min, lat_min = df['longitude'].min() - 1, df['latitude'].min() - 1
            lon_max, lat_max = df['longitude'].max() + 1, df['latitude'].max() + 1
            ax0.set_xlim([lon_min, lon_max])
            ax0.set_ylim([lat_min, lat_max])
        
        # Fallas Geográficas - Regresamos al color rojo por solicitud del usuario
        gdf_fallas.plot(ax=ax0, color='#ff0000', linewidth=0.8, alpha=0.7, label='Fallas Geológicas', zorder=2)
        
        # Puntos de sismos - Usando 'viridis' (Verde-Amarillo) que resalta mucho sobre el fondo
        scatter = ax0.scatter(df['longitude'], df['latitude'], 
                            c=df['mag'], cmap='viridis', s=20, 
                            edgecolor='white', linewidth=0.3, alpha=0.8, 
                            label='Eventos Sísmicos', zorder=3)
        
        # Añadir colorbar discreta para magnitud
        cbar = plt.colorbar(scatter, ax=ax0, orientation='vertical', shrink=0.7, pad=0.02)
        cbar.set_label('Magnitud (Mw)', fontsize=9)

        ax0.set_title('Análisis Regional: Tectónica y Actividad Sísmica (2010-2026)', fontsize=18, fontweight='bold', pad=15)
        ax0.set_xlabel('Longitud', fontsize=10, color='#495057')
        ax0.set_ylabel('Latitud', fontsize=10, color='#495057')
        ax0.grid(True, linestyle='--', alpha=0.2)
        ax0.set_facecolor('white')
        ax0.legend(loc='upper right', frameon=True, fontsize=10)

        # --- PANEL INFERIOR: TIMELINE (BAR CHART) ---
        ax1 = fig.add_subplot(gs[1])
        
        yearly_counts = df['year'].value_counts().sort_index()
        years = yearly_counts.index.astype(int)
        counts = yearly_counts.values

        # Colores dinámicos basados en la intensidad
        norm = plt.Normalize(counts.min(), counts.max())
        colors = plt.cm.YlOrRd(norm(counts))

        bars = ax1.bar(years, counts, color=colors, edgecolor='#dee2e6', linewidth=0.5)
        
        # Etiquetas de valores sobre las barras
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 5,
                    f'{int(height)}', ha='center', va='bottom', fontsize=9, fontweight='bold', color='#212529')

        ax1.set_title('Línea de Tiempo: Sismos por Año (Periodo 2010-2026)', fontsize=16, fontweight='bold', pad=10)
        ax1.set_xticks(years)
        ax1.set_xticklabels(years, rotation=45, fontsize=10)
        ax1.set_ylabel('Número de Eventos', fontsize=11)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.grid(axis='y', linestyle='--', alpha=0.3)
        ax1.set_facecolor('white')

        # Pie de página o nota informativa
        plt.figtext(0.5, 0.02, 'Fuente de datos: USGS Earthquake Catalog. Análisis realizado con metodología CRISP-DM.', 
                    ha='center', fontsize=9, style='italic', color='#6c757d')

        # 3. Guardar y mostrar
        plt.savefig(OUTPUT_IMAGE, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Visualización premium guardada en: {OUTPUT_IMAGE}")

    except Exception as e:
        print(f"❌ Error crítico en la generación de la visualización: {e}")

if __name__ == "__main__":
    generate_seismic_timeline_map()
