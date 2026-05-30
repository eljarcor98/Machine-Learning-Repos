import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load Data
url = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2020/2020-09-22/members.csv"
df = pd.read_csv(url)

# 2. Preprocessing
df['age'] = df['age'].fillna(df['age'].median())

# --- ANALYSIS 1: GENERAL POPULATION ---
print("=== ANALYSIS 1: GENERAL POPULATION ===")
features = ['age', 'sex', 'year', 'season', 'hired', 'solo', 'oxygen_used']
X = df[features]
y = df['success'].astype(int)

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), ['age', 'year', 'hired', 'solo', 'oxygen_used']),
        ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), ['sex', 'season'])
    ])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
X_train_transformed = preprocessor.fit_transform(X_train)
X_test_transformed = preprocessor.transform(X_test)

model = LogisticRegression(max_iter=1000)
model.fit(X_train_transformed, y_train)

print(f"Accuracy: {accuracy_score(y_test, model.predict(X_test_transformed)):.4f}")
print(f"ROC-AUC: {roc_auc_score(y_test, model.predict_proba(X_test_transformed)[:, 1]):.4f}")

# --- ANALYSIS 2: OXYGEN USERS ONLY ---
print("\n=== ANALYSIS 2: OXYGEN USERS ONLY ===")
df_oxy = df[df['oxygen_used'] == True].copy()
features_oxy = ['age', 'sex', 'year', 'season', 'hired', 'solo'] # removed oxygen_used
X_oxy = df_oxy[features_oxy]
y_oxy = df_oxy['success'].astype(int)

preprocessor_oxy = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), ['age', 'year', 'hired', 'solo']),
        ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), ['sex', 'season'])
    ])

X_train_o, X_test_o, y_train_o, y_test_o = train_test_split(X_oxy, y_oxy, test_size=0.2, random_state=42, stratify=y_oxy)
X_train_o_trans = preprocessor_oxy.fit_transform(X_train_o)
X_test_o_trans = preprocessor_oxy.transform(X_test_o)

model_oxy = LogisticRegression(max_iter=1000)
model_oxy.fit(X_train_o_trans, y_train_o)

print(f"Accuracy: {accuracy_score(y_test_o, model_oxy.predict(X_test_o_trans)):.4f}")
print(f"ROC-AUC: {roc_auc_score(y_test_o, model_oxy.predict_proba(X_test_o_trans)[:, 1]):.4f}")

print("\nClassification Report (Oxygen Users):")
print(classification_report(y_test_o, model_oxy.predict(X_test_o_trans)))

# Coeficientes
cat_names = preprocessor_oxy.named_transformers_['cat'].get_feature_names_out(['sex', 'season'])
all_names = ['age', 'year', 'hired', 'solo'] + list(cat_names)
coef_df = pd.DataFrame({'Variable': all_names, 'Coeficiente': model_oxy.coef_[0]}).sort_values(by='Coeficiente', ascending=False)
print("\nFeature Coefficients (Oxygen Users Only):")
print(coef_df)
