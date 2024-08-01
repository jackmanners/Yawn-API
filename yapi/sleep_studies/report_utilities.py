import os
import glob
import re

import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from striprtf.striprtf import rtf_to_text

def find_scored_folders(path, verbose=False):
    if verbose:
        print(path)
    
    # resursively search in all subdirectories for files with .slp extension or .DAT files
    # Record all tho folders that contain these files
    
    scored_folders = []
    scored_folders.extend(
        root for root, _, files in os.walk(path)
        if any('report' in file.lower() for file in files) and
        any(file.lower().endswith(('.dat', '.slp', '.rtf')) for file in files)
    )
        
    if verbose:
        print(f"Found {len(scored_folders)} scored folders...")
    
    return scored_folders

def process_folder(folder, verbose, index, total_folders):
    if verbose:
        print(f"Processing folder {index+1}/{total_folders}")
    # find all files in folder
    files = os.listdir(folder)
    # find all files that contain 'report' in the name
    report_files = [file for file in files if 'report' in file.lower()]
    
    report_data = []
    for report in report_files:
        try:
            report_path = os.path.join(folder, report)
            data = extract_data(report_path)
            report_data.append(data)
        except:
            pass
    
    return report_data

def find_reports(folders, verbose=True, **kwargs):
    report_data = []
    total_folders = len(folders)
    
    if 'limit' in kwargs and kwargs['limit'] is not None:
        folders = folders[:kwargs['limit']]
        
    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(
                process_folder, folder, verbose, i, total_folders
            ) for i, folder in enumerate(folders)]
        for future in futures:
            try:
                report_data.extend(future.result())
            except:
                pass
    
    return report_data
            
def extract_string(text, keyword, end_keyword, tabs=False):
    # Extract string between keyword and end_keyword
    pattern = rf"{keyword}(.*?){end_keyword}"
    match = re.search(pattern, text, re.DOTALL)
    value = None
    if match:
        value = match.group(1).strip()
        if tabs:
            value = value.split('\t')
            # Remove empty strings
            value = [v for v in value if v]
    return value

def extract_numeric_equals(text, keyword, extra=None):
    # Pattern to find 'keyword', followed by any characters until '=', and then capture the next number
    pattern = rf"{keyword}.*?=\s*(\d+(\.\d+)?)"
    
    match = re.search(pattern, text, flags=re.DOTALL)
    
    enums, item = (extra[0], extra[1]) if isinstance(extra, tuple) else (extra, None)
    
    if match:
        # Extract the number (either int or float)
        results = [match.group(1)]
        enum_pattern = rf".*?(\d+(\.\d+)?)"
        if enums is not None:
            for _ in range(enums):
                # find the next number after the first match
                match = re.search(enum_pattern, text[match.end():])
                if match:
                    results.append(match.group(1))
        
        if extra is not None:
            return results[item] if item else results
        else:
            return results[0]
    else:
        return None
        
def extract_data(report_path):
    # Extract data from .rtf file
    
    # Open file
    text = None
    try:
        with open(report_path, 'r') as file:
            data = file.read()
            text = rtf_to_text(data).lower()
    except UnicodeDecodeError as e:
        for encoding in ['utf-8', 'utf-16', 'cp1252', 'iso-8859-1']:
            try: 
                with open(report_path, 'r', encoding=encoding) as file:
                    data = file.read()
                    text = rtf_to_text(data).lower()
                break
            except UnicodeDecodeError as e:
                continue
    
    supine = extract_numeric_equals(text, 'supine ahi', extra=2)
    non_supine = extract_numeric_equals(text, 'non-supine ahi', extra=2)
    
    labels0 =  extract_string(text, rf'respiratory / sleep statistics.*?\n', '\n', tabs=True)
    labels1 = extract_string(text, rf'respiratory / sleep statistics.*?\n.*?\n', '\n', tabs=True)
    
    # check if labels1 is repeated (e.g., reduce [a, b, c, a, b, c] to [a, b, c])
    if labels1:
        if labels1[:len(labels1)//2] == labels1[len(labels1)//2:]:
            labels1 = labels1[:len(labels1)//2]
    
    labels = []
    if labels0 and labels1:
        for label0 in labels0:
            for label1 in labels1:
                labels.append(f"{label0}_{label1}")
                
    data = {
        'filepath': report_path,
        'patient_id': extract_string(text, 'patient:', '\n'),
        'age': extract_string(text, 'age:', '\n'),
        'sex': extract_string(text, 'sex:', '\n'),
        'study_date': extract_string(text, 'study date:', '\n'),
        'tst': extract_numeric_equals(text, 'total sleep'),
        'tib': extract_numeric_equals(text, 'time available for sleep'),
        'waso': extract_numeric_equals(text, 'total time awake during sleep'),
        'sol': extract_numeric_equals(text, 'sleep latency'),
        'rol': extract_numeric_equals(text, 'rem latency'),
        'se': extract_numeric_equals(text, 'sleep efficiency'),
        'n1': extract_numeric_equals(text, 'stage 1'),
        'n2': extract_numeric_equals(text, 'stage 2'),
        'n3': extract_numeric_equals(text, 'stage 3'),
        'n4': extract_numeric_equals(text, 'stage 4'),
        'sws': extract_numeric_equals(text, 'sws'),
        'rem': extract_numeric_equals(text, 'rem sleep'),
        'nrem': extract_numeric_equals(text, 'nrem sleep'),
        'total_ahi': extract_numeric_equals(text, 'total ahi'),
        'supine_ahi': supine[0] if supine else None,
        'non_supine_ahi': non_supine[0] if non_supine else None,
        'supine_time': supine[1] if supine else None,
        'non_supine_time': non_supine[1] if non_supine else None,
        'supine_percent': supine[2] if supine else None,
        'non_supine_percent': non_supine[2] if non_supine else None,
        'ai_resp': extract_numeric_equals(text, rf'arousal per hour:.*?\n*?respiratory'),
        'ai_limb': extract_numeric_equals(text, rf'arousal per hour:.*?limb movement'),
        'ai_spont': extract_numeric_equals(text, rf'arousal per hour:.*?spontaneous'),
        'ai_total': extract_numeric_equals(text, rf'arousal per hour:.*?total arousals'),
        'sao2_awake': extract_numeric_equals(text, 'sao2 awake average'),
    }
    
    for i, label in enumerate(labels):
        data[label+'_central_apn'] = extract_string(text, rf'ahi.*?\n*?central apnea', '\n', tabs=True)[i]
        data[label+'_obstructive_apn'] = extract_string(text, rf'ahi.*?\n*?obstructive apnea', '\n', tabs=True)[i]
        data[label+'_mixed_apn'] = extract_string(text, rf'ahi.*?\n*?mixed apnea', '\n', tabs=True)[i]
        data[label+'_hypopn'] = extract_string(text, rf'ahi.*?\n*?hypopnea', '\n', tabs=True)[i]
        data[label+'_apn_hypopn'] = extract_string(text, rf'ahi.*?\n*?apnea\+hypopnea', '\n', tabs=True)[i]
        data[label+'_sao2_min_average'] = extract_string(text, rf'sao2% min average', '\n', tabs=True)[i]
        data[label+'_sao2_lowest'] = extract_string(text, rf'sao2% lowest', '\n', tabs=True)[i]
       
    return data