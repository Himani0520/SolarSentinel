import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Create output directory
os.makedirs('eda_outputs', exist_ok=True)

files = glob.glob('*.csv')

def perform_eda(filepath):
    filename = os.path.basename(filepath)
    print(f"--- Processing {filename} ---")
    
    # Load data
    df = pd.read_csv(filepath, low_memory=False)
    
    # Parse date
    date_col = 'timestampDate' if 'timestampDate' in df.columns else 'createdAt'
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.sort_values(by=date_col)
        df.set_index(date_col, inplace=True)
        print(f"Time range: {df.index.min()} to {df.index.max()}")
        
    numeric_df = df.select_dtypes(include=[np.number])
    
    # Missing values
    missing = df.isnull().mean() * 100
    missing = missing[missing > 0].sort_values(ascending=False)
    
    with open(f'eda_outputs/{filename}_missing.txt', 'w') as f:
        f.write("Percentage of Missing Values:\n")
        f.write(missing.to_string())
        
    print(f"Saved missing value report to eda_outputs/{filename}_missing.txt")
    
    # Identify relevant columns
    power_cols = [c for c in numeric_df.columns if 'power' in c.lower() or 'pv' in c.lower()]
    temp_cols = [c for c in numeric_df.columns if 'temp' in c.lower()]
    kwh_cols = [c for c in numeric_df.columns if 'kwh' in c.lower()]
    voltage_cols = [c for c in numeric_df.columns if 'v_' in c.lower() or 'voltage' in c.lower()]
    
    # Daily aggregation for a high-level view
    if not numeric_df.empty and df.index.tz is not None:
        try:
            daily_df = numeric_df.resample('D').mean()
            
            # Plot trend of key columns
            plt.figure(figsize=(15, 6))
            if power_cols:
                daily_df[power_cols[:2]].plot(ax=plt.gca(), title=f"Daily Average Power - {filename}")
                plt.ylabel("Power")
                plt.tight_layout()
                plt.savefig(f'eda_outputs/{filename}_power_trend.png')
                plt.close()
                print(f"Saved trend plot to eda_outputs/{filename}_power_trend.png")
        except Exception as e:
            print(f"Could not resample daily for {filename}: {e}")

    # Correlation Matrix of top 20 numeric columns with highest variance
    if not numeric_df.empty:
        top_var_cols = numeric_df.var().sort_values(ascending=False).head(20).index
        corr = numeric_df[top_var_cols].corr()
        plt.figure(figsize=(12, 10))
        sns.heatmap(corr, annot=False, cmap='coolwarm')
        plt.title(f"Correlation Matrix (Top Variance Features) - {filename}")
        plt.tight_layout()
        plt.savefig(f'eda_outputs/{filename}_correlation.png')
        plt.close()
        print(f"Saved correlation matrix to eda_outputs/{filename}_correlation.png")

for f in files:
    perform_eda(f)
    print("\n")

print("EDA script finished successfully.")
