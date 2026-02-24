import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# 1. Cargar y limpiar datos
file_path = "spam.csv"

try:
    # Carga robusta
    try:
        df = pd.read_csv(file_path, encoding='latin-1')
        if 'v1' in df.columns and 'v2' in df.columns:
            df = df[['v1', 'v2']]
            df.columns = ['Label', 'Message']
    except Exception:
        df = pd.read_csv(file_path, sep='\t', names=['Label', 'Message'], encoding='latin-1')

    print(f"[INFO] Dataset cargado: {len(df)} registros.")

    # 2. Preparar variables (X e y)
    X = df['Message']
    y = df['Label']

    # 3. SPLIT TRAIN-TEST: ¿Cómo distribuirlos mejor?
    # Usamos 'stratify=y' para mantener la proporción de Spam (~13%) en ambos conjuntos.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.20, 
        random_state=42, 
        stratify=y  # CRUCIAL para datos desbalanceados
    )

    print(f"[INFO] Entrenamiento: {len(X_train)} mensajes")
    print(f"[INFO] Prueba: {len(X_test)} mensajes")

    # 4. Vectorización (Bag of Words - CountVectorizer)
    # CountVectorizer crea una matriz con la frecuencia de cada palabra.
    vectorizer = CountVectorizer(stop_words='english', lowercase=True)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # 5. Entrenamiento del Modelo (Naive Bayes Multinomial)
    model = MultinomialNB()
    model.fit(X_train_vec, y_train)

    # 6. Predicción y Evaluación
    y_pred = model.predict(X_test_vec)

    # Métricas descriptivas
    print("\n" + "="*40)
    print("      REPORTE DE CLASIFICACIÓN")
    print("="*40)
    print(classification_report(y_test, y_pred))
    
    acc = accuracy_score(y_test, y_pred)
    print(f"Exactitud Global (Accuracy): {acc:.2%}")

    # 7. Matriz de Confusión (Visualización)
    cm = confusion_matrix(y_test, y_pred, labels=['ham', 'spam'])
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Ham', 'Spam'], 
                yticklabels=['Ham', 'Spam'])
    plt.xlabel('Predicción')
    plt.ylabel('Real')
    plt.title('Matriz de Confusión - Naive Bayes')
    
    # Guardar matriz
    plt.savefig("graphs/matriz_confusion.png")
    print("\n[ÉXITO] Matriz de confusión guardada como 'graphs/matriz_confusion.png'")

    # 8. Ejemplo de prueba manual
    def predecir_mensaje(texto):
        vec = vectorizer.transform([texto])
        prob = model.predict_proba(vec)[0]
        clase = model.predict(vec)[0]
        return clase, prob

    print("\n" + "="*40)
    print("  PRUEBA DE PREDICCIÓN MANUAL")
    print("="*40)
    ejemplos = [
        "Congratulations! You won a $1000 Walmart gift card. Click here to claim.",
        "Hey, are we still meeting for lunch at 1 PM?",
        "Urgent: Your account has been compromised. Verify your details now."
    ]
    
    for msg in ejemplos:
        clase, prob = predecir_mensaje(msg)
        print(f"Mensaje: {msg[:50]}...")
        print(f"Resultado: {clase.upper()} (Ham: {prob[0]:.2%}, Spam: {prob[1]:.2%})\n")

except Exception as e:
    print(f"Error durante el entrenamiento: {e}")
    print("\nTip: Asegúrate de tener instaladas las librerías: pip install scikit-learn seaborn pandas matplotlib")
