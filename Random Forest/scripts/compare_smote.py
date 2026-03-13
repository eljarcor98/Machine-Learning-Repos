import pandas as pd
import matplotlib.pyplot as plt
import os

# Paths to datasets
original_path = r"C:\Users\Arnold's\Documents\Repositorios Machine Learning\Random Forest\data\healthcare-dataset-stroke-data.csv"
smote_path = r"C:\Users\Arnold's\Documents\Repositorios Machine Learning\Random Forest\data\healthcare-dataset-stroke-data-smote.csv"
output_image = r"C:\Users\Arnold's\Documents\Repositorios Machine Learning\Random Forest\scripts\smote_comparison.png"

# Load datasets
orig = pd.read_csv(original_path)
smote = pd.read_csv(smote_path)

target_col = "stroke"
orig_counts = orig[target_col].value_counts().sort_index()
smote_counts = smote[target_col].value_counts().sort_index()

# Plot comparison
labels = [f"Class {i}" for i in orig_counts.index]
width = 0.35
fig, ax = plt.subplots()
ax.bar([i - width/2 for i in range(len(labels))], orig_counts, width, label='Original')
ax.bar([i + width/2 for i in range(len(labels))], smote_counts, width, label='SMOTE')
ax.set_xlabel('Class')
ax.set_ylabel('Count')
ax.set_title('Class Distribution: Original vs SMOTE')
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels)
ax.legend()
fig.tight_layout()
plt.savefig(output_image)
print(f"Plot saved to {output_image}")
