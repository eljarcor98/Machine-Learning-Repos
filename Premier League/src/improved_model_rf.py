import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, confusion_matrix, classification_report
import os

def improved_model():
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

    # --- Feature Engineering ---
    def calculate_rolling_all(data, n=5):
        # Collect all relevant stats
        cols = ['GF', 'GA', 'S', 'ST', 'C', 'F', 'Y']
        
        home_side = data[['Date', 'HomeTeam', 'FTHG', 'FTAG', 'HS', 'HST', 'HC', 'HF', 'HY']].copy()
        home_side.columns = ['Date', 'Team', 'GF', 'GA', 'S', 'ST', 'C', 'F', 'Y']
        home_side['IsHome'] = 1
        
        away_side = data[['Date', 'AwayTeam', 'FTAG', 'FTHG', 'AS', 'AST', 'AC', 'AF', 'AY']].copy()
        away_side.columns = ['Date', 'Team', 'GF', 'GA', 'S', 'ST', 'C', 'F', 'Y']
        away_side['IsHome'] = 0
        
        long_df = pd.concat([home_side, away_side]).sort_values(['Team', 'Date'])
        
        # Shift(1) is vital: only use matches BEFORE today
        roll = long_df.groupby('Team')[cols].transform(lambda x: x.shift(1).rolling(n, min_periods=1).mean())
        long_df = pd.concat([long_df, roll.add_suffix('_roll')], axis=1)
        return long_df

    long = calculate_rolling_all(df)
    h_roll = long[long['IsHome']==1].copy().rename(columns={'Team': 'HomeTeam'})
    a_roll = long[long['IsHome']==0].copy().rename(columns={'Team': 'AwayTeam'})
    
    # Merge back to original matches
    df_model = df.merge(h_roll[['Date', 'HomeTeam', 'GF_roll', 'GA_roll', 'S_roll', 'ST_roll', 'C_roll', 'F_roll', 'Y_roll']], on=['Date', 'HomeTeam'])
    df_model = df_model.merge(a_roll[['Date', 'AwayTeam', 'GF_roll', 'GA_roll', 'S_roll', 'ST_roll', 'C_roll', 'F_roll', 'Y_roll']], on=['Date', 'AwayTeam'], suffixes=('_H', '_A'))
    
    # Betting probabilities
    df_model['prob_H'] = 1 / df_model['B365H']
    df_model['prob_A'] = 1 / df_model['B365A']
    df_model['market_diff'] = df_model['prob_H'] - df_model['prob_A']
    
    # --- Feature: DIFFS (Home - Away) ---
    # Tree models love differences as they represent relative strength
    for stat in ['GF_roll', 'GA_roll', 'S_roll', 'ST_roll', 'C_roll', 'F_roll', 'Y_roll']:
        df_model[f'{stat}_diff'] = df_model[f'{stat}_H'] - df_model[f'{stat}_A']
    
    base_features = [
        'GF_roll_H', 'GA_roll_H', 'ST_roll_H', 'C_roll_H', 'F_roll_H',
        'GF_roll_A', 'GA_roll_A', 'ST_roll_A', 'C_roll_A', 'F_roll_A',
        'market_diff'
    ]
    diff_features = [f'{s}_roll_diff' for s in ['GF', 'GA', 'S', 'ST', 'C', 'F', 'Y']]
    
    all_features = base_features + diff_features
    df_clean = df_model.dropna(subset=all_features + ['goal_diff'])
    
    X = df_clean[all_features]
    y = df_clean['goal_diff']

    # --- 70/30 Split ---
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=42)

    # --- Training Improved Model (Random Forest) ---
    reg = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
    reg.fit(X_train, y_train)

    # --- Evaluation ---
    y_pred = reg.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    def map_res(gd):
        if gd > 0.45: return 'H'
        if gd < -0.45: return 'A'
        return 'D'
    
    y_test_cat = df_clean.loc[y_test.index, 'FTR']
    y_pred_cat = [map_res(val) for val in y_pred]
    acc = accuracy_score(y_test_cat, y_pred_cat)

    print("--- Improved Model (Random Forest 70/30) ---")
    print(f"Features: {len(all_features)}")
    print(f"R-squared: {r2:.4f}")
    print(f"MSE: {mse:.4f}")
    print(f"Accuracy: {acc:.4f}\n")
    print(classification_report(y_test_cat, y_pred_cat))

    # --- Visuals ---
    # Importance
    importance = pd.Series(reg.feature_importances_, index=all_features).sort_values()
    plt.figure(figsize=(10, 8))
    importance.plot(kind='barh', color='purple')
    plt.title('Feature Importance (Random Forest)')
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "rf_importance.png"))

    # Confusion Matrix
    cm = confusion_matrix(y_test_cat, y_pred_cat, labels=['A', 'D', 'H'])
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='RdPu', xticklabels=['Away', 'Draw', 'Home'], yticklabels=['Away', 'Draw', 'Home'])
    plt.title('Confusion Matrix: Random Forest Outcome')
    plt.savefig(os.path.join(fig_dir, "rf_confusion_matrix.png"))

if __name__ == "__main__":
    improved_model()
