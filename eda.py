import pandas as pd
import glob
import os

files = glob.glob('c:/Users/abhi2/Desktop/HackaMind/*.csv')
for f in files:
    print(f'\n--- File: {os.path.basename(f)} ---')
    df = pd.read_csv(f, low_memory=False)
    print(f'Shape: {df.shape}')
    if 'timestampDate' in df.columns:
        print(f"Date range: {df['timestampDate'].min()} to {df['timestampDate'].max()}")
    print(f'Columns ({len(df.columns)}):')
    
    # print some basic stats on critical columns
    important_cols = [c for c in df.columns if 'pv' in c or 'power' in c or 'kwh' in c or 'temp' in c]
    if important_cols:
        print(f"Important columns summary:")
        print(df[important_cols].describe().to_string())
    else:
        print("No obvious important columns found based on keywords.")
