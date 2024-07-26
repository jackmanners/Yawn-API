import pandas as pd
import numpy as np
import ast

def main():
    file = r'C:\Users\mann0242\AppData\Local\Downloads\data_GAR_1721784148\raw_bed_Apnea Hypopnea Index.csv'
    df = pd.read_csv(file)
    
    df['start'] = pd.to_datetime(df['start'], format='%Y-%m-%dT%H:%M:%S%z', utc=True)
    df = df.sort_values(by='start')
    
    # Convert string representations of lists into actual lists
    df['duration'] = df['duration'].apply(ast.literal_eval)
    df['value'] = df['value'].apply(ast.literal_eval)
    
    # Explode the duration and value columns
    df = df.explode('duration')
    df = df.explode('value')
    
    # Ensure duration is an integer
    df['duration'] = df['duration'].astype(int)
    
    # Calculate the cumulative sum of duration for each group of start
    df['cumsum_duration'] = df.groupby('start')['duration'].cumsum()
    
    # Create the time column by adding the cumulative sum of duration to the start time
    df['time'] = df['start'] + pd.to_timedelta(df['cumsum_duration'], unit='s')
    
    # Drop the duration and cumsum_duration columns
    df = df.drop(columns=['duration', 'cumsum_duration', 'start'])
    df['value_pos'] = np.where(df['value'] < 0, 0, df['value'])
    
    print(df.head())
    df.to_csv('output.csv', index=False)
    
    
if __name__ == "__main__":
    main()