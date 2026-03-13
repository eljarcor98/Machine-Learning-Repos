import pandas as pd
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, recall_score, f1_score
from imblearn.over_sampling import SMOTE

# Paths
DATA_PATH = r"C:\Users\Arnold's\Documents\Repositorios Machine Learning\Random Forest\data\healthcare-dataset-stroke-data.csv"

# Load original data
df = pd.read_csv(DATA_PATH, na_values='N/A')

# Preprocessing
if 'id' in df.columns:
    df = df.drop(columns=['id'])

df['bmi'] = df['bmi'].fillna(df['bmi'].median())
categorical_cols = ['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']
df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

X = df_encoded.drop(columns=['stroke'])
y = df_encoded['stroke']

# Split Data (Original)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 1. Baseline Model (Imbalanced)
print("Training Baseline Model...")
rf_baseline = RandomForestClassifier(random_state=42)
rf_baseline.fit(X_train, y_train)
y_pred_baseline = rf_baseline.predict(X_test)

# 2. SMOTE Model
print("Training SMOTE Model...")
smote = SMOTE(random_state=42)
X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

rf_smote = RandomForestClassifier(random_state=42)
rf_smote.fit(X_train_res, y_train_res)
y_pred_smote = rf_smote.predict(X_test) # Note: Test on ORIGINAL data

# Comparison
def get_metrics(y_true, y_pred, name):
    return {
        "Model": name,
        "Accuracy": accuracy_score(y_true, y_pred),
        "Recall (Stroke)": recall_score(y_true, y_pred),
        "F1-Score (Stroke)": f1_score(y_true, y_pred)
    }

results = [
    get_metrics(y_test, y_pred_baseline, "Baseline (Imbalanced)"),
    get_metrics(y_test, y_pred_smote, "SMOTE Balanced")
]

print("\n--- Model Comparison ---")
results_df = pd.DataFrame(results)
print(results_df)

# Save results to a CSV for documentation if needed
# results_df.to_csv(os.path.join(os.path.dirname(DATA_PATH), "model_comparison_results.csv"), index=False)
