import os, glob, time, traceback
import pandas as pd
import numpy as np

from datetime import datetime

from yapi import YapiClient
from yapi.snapi import Withings

class epoch:
    
    def __init__(self):
        pass

    def backup_study_epoch_data(study, folder=False, verbose=False, update=False):
        if folder == True:
            # prompt user for folder using a tk dialog
            from tkinter import Tk
            from tkinter.filedialog import askdirectory
            Tk().withdraw()
            output_folder = askdirectory()
        elif type(folder) == str:
            output_folder = folder
            
        datapath = f'{study}_EpochData' if not output_folder else f'{output_folder}'
        if verbose: print(f"Output folder: {datapath}")
        # check if folder study exists in 'output' folder, and create it if not
        if not os.path.exists(datapath):
            os.makedirs(datapath)
        
        w = YapiClient.get_instance()
        withings = w.withings
        
        pxs = w.participants.get_all(study_name=study)
        pxs = [px['lab_id'] for px in pxs]
            
        # get existing files in datapath
        files = os.listdir(datapath)
        files = [file for file in files if file.endswith('.csv')]
        
        timestart = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # log a txt file to datapath showing the time updated and the participants updated
        with open(f'{datapath}/log_{timestart}.txt', 'w') as f:
            f.write(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        for i, lab_id in enumerate(pxs):
            # check if file exists with the lab_id in the name (it may have other parts to the name)
            if update:
                try:
                    px_df = pd.read_csv(f'{datapath}/{lab_id}.csv')
                    sleep_ids = px_df['w_id'].unique()
                    sleep_ids = [int(sleep_id) for sleep_id in sleep_ids]
                    if verbose: print(f"Loaded {lab_id}.csv")
                except FileNotFoundError:
                    if verbose: print(f"No file found for {lab_id}")
                    px_df = pd.DataFrame()
                    sleep_ids = []
            else:
                sleep_ids = []
                if any([lab_id in file for file in files]):
                    continue
                
            withings.sleep.update(lab_id)
            sleeps = withings.sleep.get(lab_id)
                        
            if len(sleeps) == 0 or sleeps == [[]]:
                if verbose: print(f"No sleeps for {lab_id}")
                with open(f'{datapath}/log_{timestart}.txt', 'a') as f:
                    f.write(f"\t{lab_id}: NO SLEEPS\n")
                continue
            
            try:
                sleeps = [int(sleep['w_id']) for sleep in sleeps]
            except Exception as e:
                if verbose: 
                    print(sleeps)
                    print(f"Error for {lab_id}")
                    print(e)
                    print(traceback.format_exc())
                    quit()
                # if verbose: print(sleeps)
                continue            
            
            sleeps = [sleep for sleep in sleeps if sleep not in sleep_ids]
            if verbose: print(f"Found {len(sleeps)} new sleeps for {lab_id}")
            
            with open(f'{datapath}/log_{timestart}.txt', 'a') as f:
                f.write(f"\t{lab_id}: {len(sleeps)} sleeps to add")
            
            # check if the px_nights file already exists
            if not update and os.path.exists(f'{datapath}/{lab_id}.csv'):
                continue
            
            time.sleep(1)
            px_nights = {}
            px_df = pd.DataFrame()
            
            for s, sleep in enumerate(sleeps):
                total_perc = np.round(i / len(pxs) * 100, 1)
                t1 = time.time()
                if verbose: 
                    print(f"Getting data for {lab_id} ({total_perc}%): sleep {s+1} of {len(sleeps)}", end='\r')
                try:
                    r = withings.sleep.epoch.get(lab_id, sleep)
                except:
                    if verbose: print(f"Error for {lab_id}")
                    r = withings.sleep.epoch.get(participant_id=lab_id, w_id=sleep, verbose=True)
                    print(r)
                    continue

                if 'message' in r:
                    if r['message'] == 'SNAPI token error':
                        if verbose: print(f"Token error for {lab_id}")
                        at = False
                        break
                if 'body' not in r:
                    continue
                
                if 'series' not in r['body']:
                    continue
                
                r_data = r['body']['series']
                timestamps = []
                state_list = []
                hr_list = []
                rr_list = []
                rmssd_list = []
                sdnn_1_list = []
                mvt_list = []
                
                for datum in r_data:
                    if 'state' not in datum:
                        continue
                    state = datum['state']
                    if 'hr' not in datum:
                        continue
                    hr = datum['hr']
                    for key in hr.keys():
                        timestamps.append(key)
                        state_list.append(state)
                        try:
                            hr_list.append(hr[key])
                        except:
                            hr_list.append(np.nan)
                        try:
                            rr_list.append(datum['rr'][key])
                        except:
                            rr_list.append(np.nan)
                        try:
                            rmssd_list.append(datum['rmssd'][key])
                        except:
                            rmssd_list.append(np.nan)
                        try:
                            sdnn_1_list.append(datum['sdnn_1'][key])
                        except:
                            sdnn_1_list.append(np.nan)
                        try:
                            mvt_list.append(datum['mvt_score'][key])
                        except:
                            mvt_list.append(np.nan)
                            
                sleep_df = pd.DataFrame({
                    'lab_id': [lab_id]*len(timestamps),
                    'w_id': [sleep]*len(timestamps),
                    'timestamp': timestamps,
                    'state': state_list,
                    'hr': hr_list,
                    'rr': rr_list,
                    'rmssd': rmssd_list,
                    'sdnn_1': sdnn_1_list,
                    'mvt_score': mvt_list
                })
                px_nights[sleep] = sleep_df
                
                t_elapsed = time.time() - t1
                t_sleep = 2 - t_elapsed if t_elapsed < 2 else 0.01
                
                time.sleep(t_sleep)
                
                if len(px_nights) % 10 == 0 and len(px_nights) > 0:
                    px_df = pd.concat([px_df, pd.concat(px_nights.values())], ignore_index=True)
                    px_df.drop_duplicates(subset=['lab_id', 'w_id', 'timestamp'], inplace=True)
                    px_df.to_csv(f'{datapath}/{lab_id}.csv', index=False)
                    px_nights = {}
                    
                    # get logfile, check for ' - ' and add ' - {len(px_nights)} added' if it doesn't exist
                    with open(f'{datapath}/log_{timestart}.txt', 'r') as f:
                        log = f.readlines()
                        logfill = log[:-1]
                    with open(f'{datapath}/log_{timestart}.txt', 'w') as f:
                        f.write(''.join(logfill))
                        f.write(f"\t{lab_id}: {len(sleeps)} sleeps to add - {s+1} added\n")
                        
            if len(px_nights) > 0:
                px_df = pd.concat([px_df, pd.concat(px_nights.values())], ignore_index=True)
                px_df.drop_duplicates(subset=['lab_id', 'w_id', 'timestamp'], inplace=True)
                px_df.to_csv(f'{datapath}/{lab_id}.csv', index=False)
            
            if px_df is not None and 'w_id' in px_df.columns:
                w_ids = px_df['w_id'].unique()
            else:
                w_ids = []
            
            # Check if the logfile still exists, re-create it if it doesn't
            if not os.path.exists(f'{datapath}/log_{timestart}.txt'):
                with open(f'{datapath}/log_{timestart}.txt', 'w') as f:
                    f.write(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            with open(f'{datapath}/log_{timestart}.txt', 'r') as f:
                log = f.readlines()
                logfill = log[:-1]    
            with open(f'{datapath}/log_{timestart}.txt', 'w') as f:
                f.write(''.join(logfill))
                f.write(f"\t{lab_id}: {len(sleeps)} sleeps to add - COMPLETE ({len(w_ids)} total)\n")
                
        return True

    def combine_epoch_data(study, input_folder, output_folder=None, sleep_df=None, save=True):
        
        output_folder = input_folder if output_folder is None else output_folder
        files = glob.glob(f"{input_folder}/*.csv")
        big_df = pd.DataFrame()
        if not sleep_df:
            study_df = pd.DataFrame()
            
        for file in files:
            df = pd.read_csv(file)
            # move participant_id to the first column
            cols = list(df.columns)
            cols = [cols[-1]] + cols[:-1]
            df = df[cols]
            
            df = pd.merge(df, study_df[['w_id', 'w_timezone']], on='w_id', how='left')
            df['tstamp'] = pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize('GMT')
            
            # Function to apply timezone conversion for each group
            def convert_group(group):
                timezone = group['w_timezone'].iloc[0]  # Get the timezone from the group
                group['datetime'] = group['tstamp'].dt.tz_convert(timezone).dt.tz_localize(None)
                return group
            
            # Group by 'w_timezone' and apply conversion
            grouped_df = df.groupby('w_timezone')
            grouped_df = grouped_df.apply(convert_group, include_groups=True)
            df = grouped_df.reset_index(drop=True)
            
            df.drop(['tstamp', 'timestamp'], axis=1, inplace=True)        
            
            # group by lab_id and sort by datetime within each participant, then sort by lab_id
            grouped_df = df.groupby('lab_id')
            df = grouped_df.apply(lambda x: x.sort_values('datetime'), include_groups=True).reset_index(drop=True)
            
            big_df = pd.concat([big_df, df])
        
        colorder = ['lab_id', 'w_id', 'datetime', 'w_timezone', 'state', 'hr', 'rr', 'rmssd', 'sdnn_1']
        big_df = big_df[colorder]
        
        if save:
            big_df.to_csv(f'{output_folder}/{study}_epochCombined.csv', index=False)
            
        return big_df

if __name__ == "__main__":
    pass