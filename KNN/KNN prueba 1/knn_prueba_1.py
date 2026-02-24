import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
import os

# Configuración de rutas
current_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(os.path.dirname(current_dir), 'dataset', 'iris.csv')

def cargar_datos():
    if not os.path.exists(dataset_path):
        print(f"Error: No se encontró el archivo en {dataset_path}")
        return None
    return pd.read_csv(dataset_path)

def entrenar_y_evaluar(df, max_k=30):
    # Separar X e y
    X = df.drop('species', axis=1)
    y = df['species']
    
    # Dividir dataset (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    resultados = []
    
    print(f"{'K (Vecinos)':^15} | {'Accuracy':^15}")
    print("-" * 33)
    
    # Bucle para probar diferentes K
    for k in range(1, max_k + 1):
        knn = KNeighborsClassifier(n_neighbors=k)
        knn.fit(X_train, y_train)
        y_pred = knn.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        
        resultados.append({'k': k, 'accuracy': acc})
        print(f"{k:^15} | {acc:^15.4f}")
        
    return pd.DataFrame(resultados)

def graficar_resultados(df_resultados):
    plt.figure(figsize=(10, 6))
    plt.plot(df_resultados['k'], df_resultados['accuracy'], marker='o', linestyle='-', color='b')
    plt.title('Accuracy vs Valor de K (KNN)')
    plt.xlabel('Número de Vecinos (K)')
    plt.ylabel('Precisión (Accuracy)')
    plt.xticks(range(1, 31))
    plt.grid(True)
    plt.show()

def main():
    print("--- Optimizando K para KNN en Dataset IRIS ---")
    df = cargar_datos()
    if df is not None:
        df_resultados = entrenar_y_evaluar(df, max_k=30)
        
        # Encontrar el mejor K
        mejor_k = df_resultados.loc[df_resultados['accuracy'].idxmax()]
        print("\n" + "="*40)
        print(f"Mejor resultado: K={int(mejor_k['k'])} con Accuracy={mejor_k['accuracy']:.4f}")
        print("="*40)
        
        graficar_resultados(df_resultados)

if __name__ == "__main__":
    main()
