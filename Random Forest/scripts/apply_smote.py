import pandas as pd
from imblearn.over_sampling import SMOTE
import os

# Path to the original dataset
DATA_PATH = r"C:\Users\Arnold's\Documents\Repositorios Machine Learning\Random Forest\data\healthcare-dataset-stroke-data.csv"

# Load the dataset
# BMI has 'N/A' strings which need to be treated as NaN
df = pd.read_csv(DATA_PATH, na_values='N/A')

# 1. Preprocessing
# Drop 'id' as it's just an identifier
if 'id' in df.columns:
    df = df.drop(columns=['id'])

# Target column
TARGET_COLUMN = "stroke"

# 2. Handle missing values
# BMI is often missing in this dataset
df['bmi'] = df['bmi'].fillna(df['bmi'].median())

# 3. Categorical Encoding
# SMOTE requires numeric data. We will use dummy encoding (One-Hot).
# For categorical columns: gender, ever_married, work_type, Residence_type, smoking_status
categorical_cols = ['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']
df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

# Separate features and target
X = df_encoded.drop(columns=[TARGET_COLUMN])
y = df_encoded[TARGET_COLUMN]

# 4. Apply SMOTE
smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X, y)

# Combine back into a single DataFrame
df_resampled = pd.concat([X_res, y_res], axis=1)

# Save the balanced dataset
OUTPUT_PATH = os.path.join(os.path.dirname(DATA_PATH), "healthcare-dataset-stroke-data-smote.csv")
df_resampled.to_csv(OUTPUT_PATH, index=False)

print(f"SMOTE applied successfully.")
print(f"Original class distribution:\n{y.value_counts()}")
print(f"Resampled class distribution:\n{y_res.value_counts()}")
print(f"Balanced dataset saved to: {OUTPUT_PATH}")

