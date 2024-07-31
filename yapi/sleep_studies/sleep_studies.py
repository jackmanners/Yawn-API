import os, glob
import pandas as pd

from .report_utilities import find_scored_folders, find_reports

class SleepStudies:
    def __init__(self):        
        try:
            import striprtf
        except ImportError:
            raise ImportError("Please `pip install striprtf` to use this module")
        
        self.report = Report()
    
    
class Report:        
    def collate(self, path, savepath=None, verbose=True):
        
        scored_folders = find_scored_folders(path, verbose=verbose)
        data = find_reports(scored_folders, verbose=verbose, limit=None)
        df = pd.DataFrame(data)

        # Change values to int where possible
        for col in df.columns:
            try: df[col] = pd.to_numeric(df[col])
            except: pass

        if savepath:
            df.to_csv(savepath, index=False)
        
        return df