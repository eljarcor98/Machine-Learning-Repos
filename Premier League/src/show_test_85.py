import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import os
import sys

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def print_test_results(n=85):
    base_dir = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League"
    df_path = os.path.join(base_dir, "data", "processed", "regression_dataset.csv")

    if not os.path.exists(df_path):
        print(f"Error: {df_path} not found.")
        return

    df = pd.read_csv(df_path)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df = df.sort_values('Date').reset_index(drop=True)

    # Replicate feature engineering
    def calculate_rolling_all(data, n_roll=5):
        cols = ['GF', 'GA', 'S', 'ST', 'C', 'F', 'Y']
        h = data[['Date', 'HomeTeam', 'FTHG', 'FTAG', 'HS', 'HST', 'HC', 'HF', 'HY']].copy()
        h.columns = ['Date', 'Team', 'GF', 'GA', 'S', 'ST', 'C', 'F', 'Y']
        h['IsHome'] = 1
        a = data[['Date', 'AwayTeam', 'FTAG', 'FTHG', 'AS', 'AST', 'AC', 'AF', 'AY']].copy()
        a.columns = ['Date', 'Team', 'GF', 'GA', 'S', 'ST', 'C', 'F', 'Y']
        a['IsHome'] = 0
        long_df = pd.concat([h, a]).sort_values(['Team', 'Date'])
        roll = long_df.groupby('Team')[cols].transform(lambda x: x.shift(1).rolling(n_roll, min_periods=1).mean())
        long_df = pd.concat([long_df, roll.add_suffix('_roll')], axis=1)
        return long_df

    long = calculate_rolling_all(df)
    h_roll = long[long['IsHome']==1].copy().rename(columns={'Team': 'HomeTeam'})
    a_roll = long[long['IsHome']==0].copy().rename(columns={'Team': 'AwayTeam'})
    
    df_model = df.merge(h_roll[['Date', 'HomeTeam', 'GF_roll', 'GA_roll', 'S_roll', 'ST_roll', 'C_roll', 'F_roll', 'Y_roll']], on=['Date', 'HomeTeam'])
    df_model = df_model.merge(a_roll[['Date', 'AwayTeam', 'GF_roll', 'GA_roll', 'S_roll', 'ST_roll', 'C_roll', 'F_roll', 'Y_roll']], on=['Date', 'AwayTeam'], suffixes=('_H', '_A'))
    
    df_model['prob_H'] = 1 / df_model['B365H']
    df_model['prob_A'] = 1 / df_model['B365A']
    df_model['market_diff'] = df_model['prob_H'] - df_model['prob_A']
    
    features = ['GF_roll_H', 'GA_roll_H', 'ST_roll_H', 'C_roll_H', 'GF_roll_A', 'GA_roll_A', 'ST_roll_A', 'C_roll_A', 'market_diff']
    df_clean = df_model.dropna(subset=features + ['FTR'])
    
    X = df_clean[features]
    y = df_clean['FTR']

    # Use same seed 42 to match previous evaluation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=42)

    clf = LogisticRegression(solver='lbfgs', max_iter=500)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    
    # Create the result dataframe
    results = df_clean.loc[y_test.index].copy()
    results['Predicted'] = y_pred
    results['Correct'] = (results['Predicted'] == results['FTR']).map({True: 'YES', False: 'NO'})
    
    # Select first N
    first_n = results[['Date', 'HomeTeam', 'AwayTeam', 'FTR', 'Predicted', 'Correct']].head(n)
    
    print(f"--- First {n} Results of Test Set (70/30 Split) ---")
    print(first_n.to_string(index=False))

if __name__ == "__main__":
    print_test_results(85)
