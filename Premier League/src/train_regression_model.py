import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
import os

def train_and_visualize():
    # Paths
    base_dir = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League"
    df_path = os.path.join(base_dir, "data", "processed", "regression_dataset.csv")
    fig_dir = os.path.join(base_dir, "reports", "figures")
    os.makedirs(fig_dir, exist_ok=True)

    if not os.path.exists(df_path):
        print(f"Error: {df_path} not found.")
        return

    df = pd.read_csv(df_path)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df = df.sort_values('Date')

    # --- Feature Engineering: Rolling Averages ---
    df['MatchID'] = df.index
    
    # Create rows for Home and Away perspectives to calculate performance per team
    home_stats = df[['MatchID', 'Date', 'HomeTeam', 'FTHG', 'FTAG', 'HS', 'HST']].copy()
    home_stats.columns = ['MatchID', 'Date', 'Team', 'GF', 'GA', 'S', 'ST']
    home_stats['IsHome'] = 1
    
    away_stats = df[['MatchID', 'Date', 'AwayTeam', 'FTAG', 'FTHG', 'AS', 'AST']].copy()
    away_stats.columns = ['MatchID', 'Date', 'Team', 'GF', 'GA', 'S', 'ST']
    away_stats['IsHome'] = 0
    
    long_df = pd.concat([home_stats, away_stats]).sort_values(['Team', 'Date'])
    
    # n-match rolling average
    n = 5
    cols_to_roll = ['GF', 'GA', 'S', 'ST']
    # shift(1) avoids using match itself in average
    rolling = long_df.groupby('Team')[cols_to_roll].transform(lambda x: x.shift(1).rolling(n, min_periods=1).mean())
    rolling.columns = [f"{c}_rolling" for c in cols_to_roll]
    long_df = pd.concat([long_df, rolling], axis=1)
    
    # Prepare labels for joining back to main DF
    h_rolling = long_df[long_df['IsHome'] == 1].set_index('MatchID')[[f"{c}_rolling" for c in cols_to_roll]].add_prefix('H_')
    a_rolling = long_df[long_df['IsHome'] == 0].set_index('MatchID')[[f"{c}_rolling" for c in cols_to_roll]].add_prefix('A_')
    
    # Join features back to match-level data
    df_model = df.join(h_rolling).join(a_rolling)

    # --- Feature: Market Probabilities (1/Odds) ---
    df_model['prob_H'] = 1 / df_model['B365H']
    df_model['prob_A'] = 1 / df_model['B365A']
    df_model['market_diff'] = df_model['prob_H'] - df_model['prob_A']

    # --- Cleanup: Remove rows where rolling doesn't exist yet (very first games of 2022) ---
    df_model = df_model.dropna(subset=['H_GF_rolling', 'A_GF_rolling', 'market_diff'])

    # --- Train/Test Split ---
    train = df_model[df_model['Season'] != '2425']
    test = df_model[df_model['Season'] == '2425']

    if len(test) == 0:
        print("Warning: Test set empty. Using last 20% of data as test instead.")
        split_idx = int(len(df_model) * 0.8)
        train = df_model.iloc[:split_idx]
        test = df_model.iloc[split_idx:]

    features = [
        'H_GF_rolling', 'H_GA_rolling', 'H_S_rolling', 'H_ST_rolling',
        'A_GF_rolling', 'A_GA_rolling', 'A_S_rolling', 'A_ST_rolling',
        'market_diff'
    ]
    target = 'goal_diff'

    X_train = train[features]
    y_train = train[target]
    X_test = test[features]
    y_test = test[target]

    # --- Model Training ---
    model = LinearRegression()
    model.fit(X_train, y_train)

    # --- Evaluation ---
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    def map_result(gd):
        if gd > 0.4: return 'H'
        if gd < -0.4: return 'A'
        return 'D'

    y_pred_res = [map_result(p) for p in y_pred]
    acc = accuracy_score(test['FTR'], y_pred_res)

    print(f"--- Results ---")
    print(f"Dataset Size: {len(df_model)} matches")
    print(f"Test Size: {len(test)} matches")
    print(f"R-squared: {r2:.4f}")
    print(f"Goal Diff MSE: {mse:.4f}")
    print(f"Match Outcome Accuracy (mapped): {acc:.4f}")

    # --- Visualization 1: Scatter ---
    plt.figure(figsize=(10, 6))
    sns.regplot(x=y_test, y=y_pred, scatter_kws={'alpha':0.4})
    plt.title('Actual vs Predicted Goal Difference')
    plt.xlabel('Actual Goal Difference (Home - Away)')
    plt.ylabel('Predicted Goal Difference')
    plt.axhline(0, color='red', linestyle='--', alpha=0.5)
    plt.axvline(0, color='red', linestyle='--', alpha=0.5)
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(fig_dir, "goal_diff_scatter.png"))

    # --- Visualization 2: Distribution ---
    plt.figure(figsize=(10, 6))
    sns.kdeplot(y_test, label='Actual', fill=True, color='blue')
    sns.kdeplot(y_pred, label='Predicted', fill=True, color='orange')
    plt.title('Goal Difference Distribution: Actual vs Predicted')
    plt.legend()
    plt.savefig(os.path.join(fig_dir, "goal_diff_dist.png"))
    
    # --- Importance ---
    importance = pd.Series(model.coef_, index=features).sort_values()
    plt.figure(figsize=(10, 6))
    importance.plot(kind='barh', color='teal')
    plt.title('Feature Coefficients (Model Importance)')
    plt.xlabel('Coefficient Value')
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "model_coefficients.png"))

if __name__ == "__main__":
    train_and_visualize()
