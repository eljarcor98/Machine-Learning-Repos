import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, confusion_matrix, classification_report
import os

def detailed_evaluation():
    base_dir = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League"
    df_path = os.path.join(base_dir, "data", "processed", "regression_dataset.csv")
    fig_dir = os.path.join(base_dir, "reports", "figures")
    os.makedirs(fig_dir, exist_ok=True)

    if not os.path.exists(df_path):
        print(f"Error: {df_path} not found.")
        return

    df = pd.read_csv(df_path)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df = df.sort_values('Date').reset_index(drop=True)

    # --- Feature Engineering: 5-match Rolling Averages ---
    def calculate_rolling(data):
        home_side = data[['Date', 'HomeTeam', 'FTHG', 'FTAG', 'HS', 'HST']].copy().rename(columns={'HomeTeam': 'Team', 'FTHG': 'GF', 'FTAG': 'GA', 'HS': 'S', 'HST': 'ST'})
        home_side['IsHome'] = 1
        away_side = data[['Date', 'AwayTeam', 'FTAG', 'FTHG', 'AS', 'AST']].copy().rename(columns={'AwayTeam': 'Team', 'FTAG': 'GF', 'FTHG': 'GA', 'AS': 'S', 'AST': 'ST'})
        away_side['IsHome'] = 0
        long_df = pd.concat([home_side, away_side]).sort_values(['Team', 'Date'])
        roll = long_df.groupby('Team')[['GF', 'GA', 'S', 'ST']].transform(lambda x: x.shift(1).rolling(5, min_periods=1).mean())
        long_df = pd.concat([long_df, roll.add_suffix('_rolling')], axis=1)
        return long_df

    long = calculate_rolling(df)
    h_roll = long[long['IsHome']==1].copy().rename(columns={'Team': 'HomeTeam'})
    a_roll = long[long['IsHome']==0].copy().rename(columns={'Team': 'AwayTeam'})
    
    df_model = df.merge(h_roll[['Date', 'HomeTeam', 'GF_rolling', 'GA_rolling', 'S_rolling', 'ST_rolling']], on=['Date', 'HomeTeam'])
    df_model = df_model.merge(a_roll[['Date', 'AwayTeam', 'GF_rolling', 'GA_rolling', 'S_rolling', 'ST_rolling']], on=['Date', 'AwayTeam'], suffixes=('_H', '_A'))
    
    df_model['market_diff'] = (1/df_model['B365H']) - (1/df_model['B365A'])
    
    # Define features and target
    feats = ['GF_rolling_H', 'GA_rolling_H', 'S_rolling_H', 'ST_rolling_H', 'GF_rolling_A', 'GA_rolling_A', 'S_rolling_A', 'ST_rolling_A', 'market_diff']
    df_clean = df_model.dropna(subset=feats + ['goal_diff'])
    
    X = df_clean[feats]
    y = df_clean['goal_diff']

    # --- 70/30 Split ---
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=42)

    # --- Training ---
    model = LinearRegression()
    model.fit(X_train, y_train)

    # --- Regression Metrics ---
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # --- Mapping to Categories (Ground Truth Outcome) ---
    def map_outcome(gd):
        if gd > 0.4: return 'H'  # Predicted Home Win
        if gd < -0.4: return 'A' # Predicted Away Win
        return 'D'               # Predicted Draw
    
    y_test_cat = df_clean.loc[y_test.index, 'FTR']
    y_pred_cat = [map_outcome(val) for val in y_pred]
    
    acc = accuracy_score(y_test_cat, y_pred_cat)
    labels = ['A', 'D', 'H']
    cm = confusion_matrix(y_test_cat, y_pred_cat, labels=labels)

    print("--- Detailed Evaluation (70/30 Split) ---")
    print(f"Train size: {len(X_train)} matches")
    print(f"Test size: {len(X_test)} matches")
    print(f"R-squared (Goal Diff): {r2:.4f}")
    print(f"MSE (Goal Diff): {mse:.4f}")
    print(f"Classification Accuracy (FTR): {acc:.4f}\n")
    print("Classification Report:")
    print(classification_report(y_test_cat, y_pred_cat, target_names=['Away', 'Draw', 'Home']))

    # --- Visualization 1: Scatter with Ground Truth ---
    plt.figure(figsize=(10, 6))
    sns.residplot(x=y_test, y=y_pred, lowess=True, scatter_kws={'alpha': 0.5}, line_kws={'color': 'red'})
    plt.title('Residuals Plot: Pred vs Actual Goal Difference')
    plt.xlabel('Actual Goal Difference (Ground Truth)')
    plt.ylabel('Residuals (Actual - Predicted)')
    plt.savefig(os.path.join(fig_dir, "regression_residuals.png"))

    # --- Visualization 2: Confusion Matrix Heatmap ---
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Away', 'Draw', 'Home'], yticklabels=['Away', 'Draw', 'Home'])
    plt.title('Confusion Matrix: Predicted Outcome vs Reality (Ground Truth)')
    plt.xlabel('Predicted Result')
    plt.ylabel('Actual Result (Ground Truth)')
    plt.savefig(os.path.join(fig_dir, "outcome_confusion_matrix.png"))

    # --- Visualization 3: Feature Importance (Weights) ---
    coeffs = pd.Series(model.coef_, index=feats).sort_values()
    plt.figure(figsize=(10, 6))
    coeffs.plot(kind='barh', color='darkgreen')
    plt.title('Feature Weights: What influences the model most?')
    plt.axvline(0, color='black', linewidth=0.8)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "feature_weights.png"))

if __name__ == "__main__":
    detailed_evaluation()
