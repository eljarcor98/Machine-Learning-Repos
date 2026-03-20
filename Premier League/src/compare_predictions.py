import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os
import sys

# Ensure output is UTF-8 for console consistency if possible, or just use ASCII
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def create_prediction_comparison():
    base_dir = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League"
    df_path = os.path.join(base_dir, "data", "processed", "regression_dataset.csv")
    
    if not os.path.exists(df_path):
        print(f"Error: {df_path} not found.")
        return

    df = pd.read_csv(df_path)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df = df.sort_values('Date').reset_index(drop=True)

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
    
    feats = ['GF_rolling_H', 'GA_rolling_H', 'S_rolling_H', 'ST_rolling_H', 'GF_rolling_A', 'GA_rolling_A', 'S_rolling_A', 'ST_rolling_A', 'market_diff']
    
    train = df_model[df_model['Season'] != 2425].dropna(subset=feats + ['goal_diff'])
    test = df_model[df_model['Season'] == 2425].dropna(subset=feats + ['goal_diff']).copy()
    
    model = LinearRegression().fit(train[feats], train['goal_diff'])
    
    test['pred_gd'] = model.predict(test[feats])
    
    def map_res(gd):
        if gd > 0.4: return 'H'
        if gd < -0.4: return 'A'
        return 'D'
    
    test['pred_FTR'] = test['pred_gd'].apply(map_res)
    test['correct'] = (test['pred_FTR'] == test['FTR']).map({True: 'YES', False: 'NO'})

    comparison = test[['Date', 'HomeTeam', 'AwayTeam', 'FTR', 'pred_FTR', 'correct']].tail(15)
    
    print("--- Model Comparison: Last 15 Predictions (Season 24/25) ---")
    print(comparison.rename(columns={'FTR': 'Actual', 'pred_FTR': 'Pred', 'correct': 'Hit?'}).to_string(index=False))

if __name__ == "__main__":
    create_prediction_comparison()
