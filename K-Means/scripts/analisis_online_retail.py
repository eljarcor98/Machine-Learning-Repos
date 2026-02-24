import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de la ruta del archivo
root_dir = r"C:\Users\Arnold's\Documents\Repositorios Machine Learning\K-Means"
file_path = os.path.join(root_dir, "Online Retail.xlsx")
# Carpeta específica para imágenes del EDA dentro de docs
eda_imgs_dir = os.path.join(root_dir, "docs", "eda")
os.makedirs(eda_imgs_dir, exist_ok=True)

def analyze_data():
    print("Cargando el dataset...")
    df = pd.read_excel(file_path)

    print("Procesando datos...")
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    null_counts = df.isnull().sum()

    # --- Análisis Específico ---
    print("\n--- Top 10 Países ---")
    top_countries = df['Country'].value_counts().head(10)
    
    print("\n--- Top 10 Productos ---")
    top_products_qty = df.groupby('Description')['Quantity'].sum().sort_values(ascending=False).head(10)

    # --- Generación de Gráficos ---
    print("\nGenerando visualizaciones...")
    plt.style.use('ggplot')
    
    # 1. Gráfico de Países
    plt.figure(figsize=(12, 6))
    sns.barplot(x=top_countries.values, y=top_countries.index, hue=top_countries.index, legend=False, palette='viridis')
    plt.title('Top 10 Países por Número de Transacciones')
    plt.xlabel('Cantidad de Transacciones')
    plt.tight_layout()
    plt.savefig(os.path.join(eda_imgs_dir, "top_paises.png"))
    plt.close()

    # 2. Gráfico de Productos
    plt.figure(figsize=(12, 6))
    sns.barplot(x=top_products_qty.values, y=top_products_qty.index, hue=top_products_qty.index, legend=False, palette='magma')
    plt.title('Top 10 Productos más Vendidos (Cantidad)')
    plt.xlabel('Unidades Vendidas')
    plt.tight_layout()
    plt.savefig(os.path.join(eda_imgs_dir, "top_productos.png"))
    plt.close()

    # --- Análisis de Tiempo (Horas) ---
    df['Hour'] = df['InvoiceDate'].dt.hour
    hourly_sales = df['Hour'].value_counts().sort_index()

    print("Generando gráfico de horas...")
    plt.figure(figsize=(12, 6))
    sns.lineplot(x=hourly_sales.index, y=hourly_sales.values, marker='o', color='teal')
    plt.title('Distribución de Transacciones por Hora del Día')
    plt.xlabel('Hora (24h)')
    plt.ylabel('Nº de Transacciones')
    plt.xticks(range(6, 21)) # La mayoría de ventas ocurren entre 6am y 8pm
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(eda_imgs_dir, "ventas_por_hora.png"))
    plt.close()

    # --- Análisis de Valores Negativos ---
    neg_qty = df[df['Quantity'] < 0]
    neg_price = df[df['UnitPrice'] < 0]

    # --- Análisis de Outliers (Boxplots) ---
    print("Analizando valores atípicos (Boxplots)...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Boxplot de Cantidad
    sns.boxplot(y=df['Quantity'], ax=ax1, color='salmon')
    ax1.set_title('Distribución de Cantidad (Quantity)')
    
    # Boxplot de Precio Unitario
    sns.boxplot(y=df['UnitPrice'], ax=ax2, color='lightblue')
    ax2.set_title('Distribución de Precio Unitario (UnitPrice)')
    
    plt.tight_layout()
    plt.savefig(os.path.join(eda_imgs_dir, "outliers_boxplots.png"))
    plt.close()

    # Boxplot filtrado para ver mejor la distribución central (sin extremos masivos)
    print("Generando boxplots filtrados...")
    df_filtered = df[(df['Quantity'].between(-100, 100)) & (df['UnitPrice'].between(0, 50))]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    sns.boxplot(y=df_filtered['Quantity'], ax=ax1, color='salmon')
    ax1.set_title('Cantidad (Filtrado -100 a 100)')
    
    sns.boxplot(y=df_filtered['UnitPrice'], ax=ax2, color='lightblue')
    ax2.set_title('Precio Unitario (Filtrado 0 a 50)')
    
    plt.tight_layout()
    plt.savefig(os.path.join(eda_imgs_dir, "outliers_filtrados.png"))
    plt.close()

    # --- Análisis de Variedad de Productos ---
    print("Analizando variedad de productos...")
    unique_prods_country = df.groupby('Country')['StockCode'].nunique().sort_values(ascending=False).head(10)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(x=unique_prods_country.values, y=unique_prods_country.index, hue=unique_prods_country.index, legend=False, palette='coolwarm')
    plt.title('Variedad de Productos (SKUs Únicos) por País - Top 10')
    plt.xlabel('Número de Productos Diferentes')
    plt.tight_layout()
    plt.savefig(os.path.join(eda_imgs_dir, "variedad_productos.png"))
    plt.close()

    # --- Análisis de compras por usuario (incluyendo sin ID) ---
    print("Analizando frecuencia por usuario...")
    df_users = df.copy()
    df_users['CustomerID_Filled'] = df_users['CustomerID'].fillna('Guest').astype(str)
    user_purchases = df_users.groupby('CustomerID_Filled')['InvoiceNo'].nunique().sort_values(ascending=False)
    
    print("Generando gráfico de frecuencia de usuarios...")
    plt.figure(figsize=(12, 6))
    top_n_users = user_purchases.head(11) 
    colors = ['orange' if x == 'Guest' else 'skyblue' for x in top_n_users.index]
    sns.barplot(x=top_n_users.index, y=top_n_users.values, hue=top_n_users.index, legend=False, palette=colors)
    plt.title('Top Usuarios por Frecuencia de Compra (Incluye Guests)')
    plt.xlabel('ID Cliente (o Guest)')
    plt.ylabel('Número de Compras Únicas')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(eda_imgs_dir, "frecuencia_usuarios.png"))
    plt.close()

    # --- Análisis de Relaciones (Pairplot) ---
    print("Generando pairplot (esto puede tardar un poco)...")
    # Usamos una muestra y los datos filtrados para que el gráfico sea legible y rápido
    df_sample = df_filtered.sample(n=min(5000, len(df_filtered)), random_state=42)
    
    plt.figure(figsize=(10, 10))
    pair_plot = sns.pairplot(df_sample[['Quantity', 'UnitPrice', 'TotalPrice']], diag_kind='kde', plot_kws={'alpha': 0.5})
    pair_plot.fig.suptitle('Relaciones entre Variables Numéricas (Muestra Filtrada)', y=1.02)
    
    pair_plot.savefig(os.path.join(eda_imgs_dir, "pairplot_relaciones.png"))
    plt.close()

    # Cálculos Finales
    total_revenue = df['TotalPrice'].sum()
    top_customers = df.groupby('CustomerID')['TotalPrice'].sum().sort_values(ascending=False).head(10)

    # --- Actualizar EDA_ONLINE_RETAIL.md ---
    eda_path = os.path.join(root_dir, "docs", "EDA_ONLINE_RETAIL.md")
    with open(eda_path, "w", encoding="utf-8") as f:
        f.write("# Análisis Exploratorio de Datos (EDA) - Online Retail\n\n")
        
        f.write("## 1. Resumen de Operaciones\n")
        f.write(f"- **Registros procesados:** {df.shape[0]:,}\n")
        f.write(f"- **Productos Únicos (SKUs):** {df['StockCode'].nunique():,}\n")
        f.write(f"- **Ingresos Totales:** {total_revenue:,.2f}\n")
        f.write(f"- **Periodo:** {df['InvoiceDate'].min().strftime('%Y-%m-%d')} a {df['InvoiceDate'].max().strftime('%Y-%m-%d')}\n\n")

        f.write("## 2. Definición de Variables y Naturaleza\n")
        f.write("| Columna | Tipo de Dato | Naturaleza | Descripción |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        
        naturalezas = {
            'InvoiceNo': 'Categórica', 'StockCode': 'Categórica', 'Description': 'Categórica',
            'Quantity': 'Numérica (Discreta)', 'InvoiceDate': 'Temporal', 'UnitPrice': 'Numérica (Continua)',
            'CustomerID': 'Categórica (ID)', 'Country': 'Categórica', 'TotalPrice': 'Numérica (Continua)',
            'Hour': 'Numérica (Ordinal)'
        }

        for col in [c for c in df.columns if c in naturalezas]:
            dtype = str(df[col].dtype)
            nat = naturalezas.get(col)
            desc = "Variable del dataset"
            if col == 'TotalPrice': desc = "Cálculo: Quantity * UnitPrice"
            if col == 'Hour': desc = "Hora extraída de InvoiceDate"
            f.write(f"| **{col}** | {dtype} | {nat} | {desc} |\n")
        f.write("\n")

        f.write("## 3. Métricas Estadísticas (Numéricas)\n")
        stats = df[['Quantity', 'UnitPrice', 'TotalPrice']].describe().transpose()
        f.write("| Métrica | Quantity | UnitPrice | TotalPrice |\n| :--- | :--- | :--- | :--- |\n")
        f.write(f"| **Media** | {stats.at['Quantity', 'mean']:.4f} | {stats.at['UnitPrice', 'mean']:.2f} | {stats.at['TotalPrice', 'mean']:.2f} |\n")
        f.write(f"| **Mediana** | {stats.at['Quantity', '50%']:.2f} | {stats.at['UnitPrice', '50%']:.2f} | {stats.at['TotalPrice', '50%']:.2f} |\n")
        f.write(f"| **Desv. Est.** | {stats.at['Quantity', 'std']:.2f} | {stats.at['UnitPrice', 'std']:.2f} | {stats.at['TotalPrice', 'std']:.2f} |\n\n")

        f.write("## 4. Análisis de Outliers (Valores Atípicos)\n")
        f.write("![Outliers Totales](eda/outliers_boxplots.png)\n")
        f.write("![Outliers Filtrados](eda/outliers_filtrados.png)\n\n")

        f.write("## 5. Correlaciones y Relaciones\n")
        f.write("![Pairplot Relaciones](eda/pairplot_relaciones.png)\n\n")

        f.write("## 6. Calidad de Datos\n")
        f.write(f"- **Registros con cantidad negativa:** {len(neg_qty):,}\n")
        f.write(f"- **Clientes sin ID:** {null_counts['CustomerID']:,} ({null_counts['CustomerID']/len(df)*100:.2f}%)\n\n")

        f.write("## 7. Visualizaciones Clave\n")
        f.write("### 7.1 Variedad de Productos por País\n")
        f.write("![Variedad Productos](eda/variedad_productos.png)\n\n")
        f.write("### 7.2 Distribución Geográfica\n")
        f.write("![Top Países](eda/top_paises.png)\n\n")
        f.write("### 7.3 Comportamiento Temporal\n")
        f.write("![Ventas por Hora](eda/ventas_por_hora.png)\n\n")
        f.write("### 7.4 Análisis de Clientes (ID vs Guests)\n")
        f.write("![Frecuencia Usuarios](eda/frecuencia_usuarios.png)\n\n")

        f.write("## 8. Top 10 Clientes (Monetario)\n")
        f.write("| ID Cliente | Gasto Total |\n|------------|-------------|\n")
        for cid, spent in top_customers.items():
            if pd.isna(cid): continue
            f.write(f"| {int(cid)} | {spent:,.2f} |\n")

        f.write("\n## 9. Conclusiones para K-Means\n")
        f.write("1. **Tratamiento de Outliers:** Limpiar extremos.\n2. **Limpieza:** Filtrar negativos.\n3. **Identificación:** Manejo de Guests.\n")

    print(f"\nProceso finalizado. Imágenes en: {eda_imgs_dir}")
    print(f"Reporte EDA actualizado en: {eda_path}")

if __name__ == "__main__":
    analyze_data()
