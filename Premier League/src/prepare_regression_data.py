import pandas as pd
import os

def prepare_data():
    base_dir = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Premier League"
    raw_dir = os.path.join(base_dir, "data", "raw")
    processed_dir = os.path.join(base_dir, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)

    files = ["pl_2223.csv", "pl_2324.csv", "pl_2425.csv"]
    all_data = []

    for f in files:
        path = os.path.join(raw_dir, f)
        if os.path.exists(path):
            print(f"Loading {f}...")
            df = pd.read_csv(path)
            # Add season info
            df['Season'] = f.split('_')[1].split('.')[0]
            all_data.append(df)
        else:
            print(f"Warning: {f} not found.")

    if not all_data:
        print("No data found to process.")
        return

    combined_df = pd.concat(all_data, ignore_index=True)

    # 1. Target Variable: Goal Difference
    combined_df['goal_diff'] = combined_df['FTHG'] - combined_df['FTAG']

    # 2. Target Variable: Result Points (for Home Team perspective)
    def get_points(res):
        if res == 'H': return 3
        if res == 'D': return 1
        return 0
    
    combined_df['result_points'] = combined_df['FTR'].apply(get_points)

    # Select relevant columns for the model
    # Identity: Div, Date, HomeTeam, AwayTeam
    # Target: goal_diff, result_points, FTR
    # Core predictors: HS, AS, HST, AST, HC, AC, HF, AF, HY, AY
    # Odds: B365H, B365D, B365A
    cols_to_keep = [
        'Season', 'Div', 'Date', 'HomeTeam', 'AwayTeam', 
        'FTHG', 'FTAG', 'FTR', 'goal_diff', 'result_points',
        'HS', 'AS', 'HST', 'AST', 'HC', 'AC',
        'HF', 'AF', 'HY', 'AY',
        'B365H', 'B365D', 'B365A'
    ]
    
    final_cols = [c for c in cols_to_keep if c in combined_df.columns]
    final_df = combined_df[final_cols]

    output_path = os.path.join(processed_dir, "regression_dataset.csv")
    final_df.to_csv(output_path, index=False)
    print(f"Dataset updated successfully at {output_path}")
    print(f"Shape: {final_df.shape}")

if __name__ == "__main__":
    prepare_data()
