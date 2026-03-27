import pandas as pd
import glob
import os
import numpy as np

def clean_and_feature_engineer(file_path):
    print(f"Processing {file_path}...")
    df = pd.read_csv(file_path, low_memory=False)
    
    # 1. Date parsing
    date_col = 'timestampDate' if 'timestampDate' in df.columns else 'createdAt'
    if date_col not in df.columns:
        print("No date column found, skipping.")
        return None
        
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col])
    df = df.sort_values(by=date_col)
    
    # Set index
    df.set_index(date_col, inplace=True)
    
    # 2. Drop high missing values (>50%)
    missing_pct = df.isnull().mean()
    cols_to_drop = missing_pct[missing_pct > 0.50].index
    df = df.drop(columns=cols_to_drop)
    
    # Drop non-numeric useless columns
    numeric_df = df.select_dtypes(include=[np.number]).copy()
    
    # Drop duplicate indexes
    numeric_df = numeric_df[~numeric_df.index.duplicated(keep='first')]
    
    # Forward fill timeseries gaps
    numeric_df = numeric_df.ffill().bfill()
    
    # 3. Add Time Features
    numeric_df['hour'] = numeric_df.index.hour
    numeric_df['month'] = numeric_df.index.month
    numeric_df['dayofweek'] = numeric_df.index.dayofweek
    
    # 4. Create Target Label (Risk of failure/underperformance in next 7 days)
    # We define failure as alarm_code > 0 OR daily power is 0 when it should be sunny.
    # To keep it robust, let's use alarm_code and op_state as ground truth if available.
    
    alarm_cols = [c for c in numeric_df.columns if 'alarm_code' in c.lower() or 'op_state' in c.lower()]
    if alarm_cols:
        # If any alarm code > 0, we assume failure/anomaly
        numeric_df['is_failure'] = (numeric_df[alarm_cols] > 0).any(axis=1).astype(int)
    else:
        # Fallback: if power is 0 during daylight hours (10 AM to 2 PM)
        power_cols = [c for c in numeric_df.columns if 'power' in c.lower() and 'pv' in c.lower()]
        if power_cols:
            main_power = power_cols[0]
            is_day = (numeric_df['hour'] >= 10) & (numeric_df['hour'] <= 14)
            numeric_df['is_failure'] = ((numeric_df[main_power] <= 0) & is_day).astype(int)
        else:
            numeric_df['is_failure'] = 0
            
    # Now create the multi-horizon lookahead targets
    # We want to predict if there is a failure within the NEXT X hours/days.
    horizons = ['6h', '12h', '24h', '1D', '2D', '3D', '4D', '5D', '6D', '7D']
    
    for h in horizons:
        col_name = f'target_{h}_failure'
        # rolling max over next 'h' period. Shift backwards so row T predicts T to T+h
        # Using shift with freq doesn't align indexes easily. A cleaner way for timeseries 
        # is to forward-roll and then shift backwards by the equivalent number of rows, 
        # or use index-based slice rolling if the index is strictly continuous.
        # But pandas rolling with an offset string assumes looking backwards.
        
        # To look forward: we reverse the dataframe, do a backwards rolling window (which is 
        # technically forwards in time), and reverse back.
        rev_df = numeric_df[::-1]
        rolled = rev_df['is_failure'].rolling(window=h, min_periods=1).max()
        numeric_df[col_name] = rolled[::-1]
        
        numeric_df[col_name] = numeric_df[col_name].fillna(0).astype(int)
    
    # Drop original is_failure to prevent data leakage if predicting
    # Also drop alarm codes from features
    numeric_df = numeric_df.drop(columns=['is_failure'] + alarm_cols, errors='ignore')
    
    # Save to disk
    out_name = f"src/data/processed_{os.path.basename(file_path)}"
    numeric_df.to_csv(out_name)
    print(f"Saved processed dataset to {out_name}, Shape: {numeric_df.shape}")
    
    return out_name

if __name__ == '__main__':
    files = glob.glob('*.csv')
    if not os.path.exists('src/data'):
        os.makedirs('src/data')
        
    for f in files:
        clean_and_feature_engineer(f)
    
    print("Preprocessing completed successfully!")
