import pandas as pd
import plotly.express as px
import os

# Cargar el dataset
path = 'data/earthquakes_raw.csv'

def create_interactive_map():
    try:
        df = pd.read_csv(path)
        
        # Preprocesamiento de tiempo
        df['time'] = pd.to_datetime(df['time'])
        df['year_month'] = df['time'].dt.strftime('%Y-%m')
        df = df.sort_values('time')
        
        print("Generando mapa interactivo con línea de tiempo...")
        
        # Crear la animación con Plotly
        fig = px.scatter_mapbox(
            df, 
            lat="latitude", 
            lon="longitude", 
            size="mag", 
            color="mag",
            hover_name="place", 
            hover_data={
                "mag": True, 
                "depth": True, 
                "time": True,
                "latitude": False,
                "longitude": False
            },
            animation_frame="year_month",
            color_continuous_scale=px.colors.sequential.Reds,
            size_max=15, 
            zoom=4.5,
            center={"lat": 4.5709, "lon": -74.2973}, # Centro de Colombia
            mapbox_style="carto-positron",
            title="Sismos en Colombia y Alrededores (2010-2026)",
            labels={'mag': 'Magnitud', 'depth': 'Profundidad (km)', 'year_month': 'Año-Mes'}
        )
        
        # Ajustar el diseño
        fig.update_layout(
            margin={"r":0,"t":50,"l":0,"b":0},
            updatemenus=[{
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}],
                        "label": "Reproducir",
                        "method": "animate"
                    },
                    {
                        "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                        "label": "Pausar",
                        "method": "animate"
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }]
        )
        
        # Guardar en la carpeta de documentación
        output_file = 'documentacion/mapa_sismos.html'
        fig.write_html(output_file)
        
        print(f"Mapa interactivo generado exitosamente: {output_file}")
        
    except Exception as e:
        print(f"Error al generar el mapa: {e}")

if __name__ == "__main__":
    create_interactive_map()
