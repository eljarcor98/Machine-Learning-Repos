import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_visuals():
    # Rutas
    base_dir = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League"
    data_path = os.path.join(base_dir, 'data', 'raw', 'pl_2324.csv') # Usamos 23/24 por ser una temporada completa
    output_dir = os.path.join(base_dir, 'reports', 'figures')
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(data_path):
        print(f"Error: {data_path} no encontrado.")
        return

    df = pd.read_csv(data_path)
    sns.set_theme(style="whitegrid", palette="muted")
    
    # 1. Home vs Away Advantage
    plt.figure(figsize=(10, 6))
    res_count = df['FTR'].value_counts().sort_index()
    res_map = {'A': 'Away Win', 'D': 'Draw', 'H': 'Home Win'}
    res_count.index = [res_map[i] for i in res_count.index]
    
    plt.pie(res_count, labels=res_count.index, autopct='%1.1f%%', startangle=140, colors=['#ff9999','#66b3ff','#99ff99'])
    plt.title('Distribución de Resultados (Temporada 23/24)')
    plt.savefig(os.path.join(output_dir, 'home_advantage.png'))
    plt.close()
    
    # 2. Shots vs Goals (Shot Efficiency)
    plt.figure(figsize=(10, 6))
    subset = df[['HS', 'AS', 'FTHG', 'FTAG']].copy()
    subset['Total Shots'] = subset['HS'] + subset['AS']
    subset['Total Goals'] = subset['FTHG'] + subset['FTAG']
    
    sns.regplot(data=subset, x='Total Shots', y='Total Goals', scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
    plt.title('Correlación: Tiros Totales vs Goles Totales')
    plt.savefig(os.path.join(output_dir, 'shots_vs_goals.png'))
    plt.close()
    
    # 3. Disciplinary Stats (Cards)
    plt.figure(figsize=(10, 6))
    cards = pd.melt(df[['HY', 'AY', 'HR', 'AR']])
    cards['Type'] = cards['variable'].apply(lambda x: 'Yellow' if 'Y' in x else 'Red')
    cards['Side'] = cards['variable'].apply(lambda x: 'Home' if x.startswith('H') else 'Away')
    
    sns.barplot(data=cards, x='Type', y='value', hue='Side', estimator=sum, errorbar=None)
    plt.title('Total de Tarjetas: Local vs Visitante')
    plt.savefig(os.path.join(output_dir, 'disciplinary_stats.png'))
    plt.close()
    
    # 4. Heatmap de Correlación
    plt.figure(figsize=(12, 10))
    cols = ['FTHG', 'FTAG', 'HS', 'AS', 'HST', 'AST', 'HC', 'AC', 'HF', 'AF', 'HY', 'AY']
    corr = df[cols].corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Mapa de Correlación de Métricas de Juego')
    plt.savefig(os.path.join(output_dir, 'correlation_heatmap.png'))
    plt.close()
    
    print(f"Visualizaciones generadas exitosamente en: {output_dir}")

if __name__ == "__main__":
    generate_visuals()
