import os
import glob
import re

import pandas as pd
from striprtf.striprtf import rtf_to_text

def find_scored_folders(path, verbose=False):
    if verbose:
        print(path)
    
    # resursively search in all subdirectories for files with .slp extension or .DAT files
    # Record all tho folders that contain these files
    
    scored_folders = []
    for root, dirs, files in os.walk(path):\
        # check if folder contains both a file with 'report' in the name and a .DAT or .SLP file
        if any(
            'report' in file.lower() for file in files) and any(
                file.lower().endswith('.DAT') or file.lower().endswith('.slp') for file in files):
            scored_folders.append(root)
    
    if verbose:
        print(f"Found {len(scored_folders)} scored folders...")
    
    return scored_folders

def find_reports(folders, verbose=True):
    
    report_data = []
    
    for i, folder in enumerate(folders):
        if verbose:
            print(f"Processing folder {i+1}/{len(folders)}", end='\r')
        # find all files in folder
        files = os.listdir(folder)
        # find all files that contain 'report' in the name
        report_files = [file for file in files if 'report' in file.lower()]
        
        for report in report_files:
            report_path = os.path.join(folder, report)
            data = extract_data(report_path)
            report_data.append(data)
        
        if verbose and i < len(folders)-1:
            print(' '*len(f"Processing folder {i+1}/{len(folders)}"), end='\r')
        elif verbose:
            print(' '*len(f"Processing folder {i+1}/{len(folders)}"), end='\r')
            
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
    return value

def extract_numeric_equals(text, keyword, extra=None):
    # Pattern to find 'keyword', followed by any characters until '=', and then capture the next number
    pattern = rf"{keyword}.*?=\s*(\d+(\.\d+)?)"
    
    match = re.search(pattern, text)
    
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
        'central_apn': extract_string(text, rf'ahi.*?\ncentral apnea', '\n', tabs=True),
        'obstructive_apn': extract_string(text, rf'ahi.*?\nobstructive apnea', '\n', tabs=True),
        'mixed_apn': extract_string(text, rf'ahi.*?\nmixed apnea', '\n', tabs=True),
        'hypopn': extract_string(text, rf'ahi.*?\nhypopnea', '\n', tabs=True),
        'apn_hypopn': extract_string(text, rf'ahi.*?\napnea+hypopnea', '\n', tabs=True),
        'ai_resp': extract_numeric_equals(text, rf'arousals per hour:.*?respiratory'),
        'ai_limb': extract_numeric_equals(text, rf'arousals per hour:.*?limb movement'),
        'ai_spont': extract_numeric_equals(text, rf'arousals per hour:.*?spontaneous'),
        'ai_total': extract_numeric_equals(text, rf'arousals per hour:.*?total arousals'),
        'sleep_stats_lables0': extract_string(text, rf'respiratory / sleep statistics.*?\n', '\n', tabs=True),
        'sleep_stats_lables1': extract_string(text, rf'respiratory / sleep statistics.*?\n.*?\n', '\n', tabs=True),
        'sao2_min_average': extract_string(text, rf'sao2% min average', '\n', tabs=True),
        'sao2_lowest': extract_string(text, rf'sao2% lowest', '\n', tabs=True),
        'sao2_awake': extract_numeric_equals(text, 'sao2 awake average'),
    }
    
    return data