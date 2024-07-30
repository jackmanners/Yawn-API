import os, glob
import pandas as pd

class InquisitClient:
    def __init__(self, verbose=False):
        self._verbose = verbose
        
    
    def collate(
        self, path, savepath=None, recursive=True,
        test='', filepath=False, identifier:tuple=None):
        
        if recursive:
            files = glob.glob(os.path.join(path, '**', f'*.iqdat'), recursive=True)
        else:
            files = glob.glob(os.path.join(path, '*.iqdat'))
        
        summary_data = []
        raw_data = []        
        
        for i, file in enumerate(files):
            if len(test) > 0 and test.lower() not in file.lower():
                continue
            
            filename = os.path.basename(file)
            if self._verbose:
                print(f'Processing file {i+1}/{len(files)}: {filename}', end='\r')
                
            df = pd.read_csv(file, sep='\t')
            
            if filepath:
                df['filepath'] = file
            
            if 'subjectid' in df.columns:
                df['participant'] = df['subjectid'].apply(self.extract_participant_id)
            else:
                df['participant'] = df['subject'].apply(self.extract_participant_id)
                
            df.insert(0, 'participant', df.pop('participant'))
            if identifier is not None:
                df[identifier[0]] = identifier[1]
                df.insert(1, identifier[0], df.pop(identifier[0]))
                            
            if '_summary' in file:
                summary_data.append(df)
            else:
                raw_data.append(df)
                
            if self._verbose and i < len(files)-1:
                print(' '*len(f'Processing file {i+1}/{len(files)}: {filename}'), end='\r')
            elif self._verbose:
                print(' '*len(f'Processing file {i+1}/{len(files)}: {filename}'), end='\r')
                
        summary_df = pd.concat(summary_data, ignore_index=True)
        raw_df = pd.concat(raw_data, ignore_index=True)
        
        if savepath:
            
            if not savepath.endswith('/'):
                savepath += '/'
            if not os.path.exists(savepath):
                os.makedirs(savepath)
            
            testname = f"{test}_" if len(test) > 0 else ''
            
            summary_df.to_csv(f"{savepath}{testname}combinedSummary.csv", index=False)
            raw_df.to_csv(f"{savepath}{testname}combinedRaw.csv", index=False)
            
        if self._verbose:
            print(f"Processed {len(files)} files")
            
        return summary_df, raw_df
    

    def extract_participant_id(self, identifier):
        identifier_str = str(identifier)
        if '_' in identifier_str:
            return identifier_str.split('_')[0]
        elif ' ' in identifier_str:
            return identifier_str.split(' ')[0]
        else:
            return identifier_str