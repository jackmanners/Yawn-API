# Yawn-API (yapi)

[![PyPI version](https://badge.fury.io/py/yawn-api.svg)](https://badge.fury.io/py/yawn-api)

A Python package for interacting with the SNAPI API, YawnLabs, and various other health device APIs.

## Installation

Install via Github using `pip install`:

```bash
pip install yawn-api
```

## Usage

Primarily interfaces with the SNAPI API, but also has some functionality for directly accessing device-specific APIs.
By default data is rethieved in JSON format, but can be returned as a response object by setting `verbose=True`.

```python
from yapi import YapiClient

# Verbose mode will print more information to the console and is useful for debugging. 

# NOTE: Will also return responses as response objects, rather than json, 
# so subsequent functionality may be impacted.

# yp = YapiClient(verbose=True) 
yp = YapiClient()

sleeps = yp.withings.sleep.get('participant1')
print(sleeps)

```

### Utilities

YAPI has a number of helper functions for working with the data returned by the API.
For example, the below gets participants information for the associated study and then requests sleep summary information based on the participant IDs.\\
The function `epoch.backup_study_epoch_data` is then called to retrieve epoch data for each participant directly from Withings and save them to individual .csv files.\\
Finally, `epoch.combine_epoch_data` is called to combine the individual .csv files into a single DataFrame.

```python
from yapi import YapiClient

yp = YapiClient()
study = 'SAMOSA'

study_participants = yp.participants.get_all(study_name=study)
participant_ids = [participant['lab_id'] for participant in study_participants]

sleeps = yp.withings.sleep.get(participant_ids, as_df=True)

path = '/path/for/epoch/data'

epoch.backup_study_epoch_data(
    study=study,    # Required - the name of the study.
    folder=path,    # Optional - if False, will create a directory f'{study}_EpochData' in the current working directory. 
                    # If True, will open a file dialog to select the folder. Otherwise, specify the path to the folder.
    verbose=True,   # Optional - print more information to the console.
    update=True     # Optional - update the epoch data if it already exists, 
                    # otherwise will skip any existing files in the folder.
)

# Inclusion of the sleep_df argument will combine the timezone information from the sleep data.
# This is not necessary, but can be useful with interpretation. If unsure, it is recommended to include it.
epoch_data = epoch.combine_epoch_data(
    study=study,        # Required - the name of the study.
    input_folder=path,  # Required - the folder to save the epoch data to.
    output_folder=path, # Optional - the folder to save the epoch data to, defaults to the input folder.
    sleep_df=sleeps,    # Optional - the sleep data to include timezone information from. 
                        # If not included, will still combine the epoch data, but will not include timezone information.
    save=True           # Optional - save the combined epoch data to a '{study}_epochCombined.csv' file in the output folder.
)

print(epoch_data.head())
```

### RedCap

YAPI also has a number of helper functions for working with the RedCap API.

For example, the below will get all records from a RedCap project, filter out to only includethose that have consented, and then create participant entries in the YawnLabs database for each of them.

```python
from yapi.redcap import RedcapClient

token = 'redcap_token'  # Required - the API token for the RedCap project.
yrc = RedcapClient(token=token) 

r = yrc.records.get()
consented = [record for record in r if record['checkconsent'] == '1']

for participant in consented:
    yp.participants.create({
        'lab_id': participant['lab_id'],
        'study_name': 'MIMOSA'
    })

```

Alternatively, the below will get a file from a RedCap project and save it to the current working directory.

```python
from yapi.redcap import RedcapClient

yrc = RedcapClient(token=s)
response = ypr.files.get(
    record_id='SAMOSA036',      # Required - the record ID in the RedCap project.
    field='cpap_upload',        # Required - the field name in the RedCap project.
    event='recruitment_arm_1'   # Required for longitudinal projects, only.
)

ypr.files.save(
    response,
    filename='test',# The extension can be automatically inferred from the 
                    # response object, or specified manually 
                    # (e.g., filename='test.pdf').
    filepath='/data'# Optional - the path to save the file to. 
                    # Defaults to the current working directory.
)

```

### Inquisit

YAPI also has some helper functions for working with the Inquisit API.
For now, this is primarily for collating Inquisit `.iqdat` files into a single DataFrame, but more will be added as time allows.

```python
from yapi.inquisit import InquisitClient

yiq = InquisitClient()

path = '/path/to/iqdat/files'
savepath = '/path/to/save/combined/file'
pvt_summary, pvt_raw = yiq.collate(
    path=path,          # Required - the path to the folder containing the .iqdat files.
    test='PVT',         # Optional - the name of the test to collate. 
                        # If not specified, will attempt to collate all tests in the folder.
                        # NOTE: this must match (or be in) the name of the test in the .iqdat files (case-insensitive).
                        # For example, 'PVT' will match 'PVT', 'pvt', 'PVT_1', 'PVT_2', etc.
    savepath=savepath   # Optional - the path to save the combined file to. 
                        # If not specified, will not save the file.
)
```

Below is a more complex example that collates PVT and Digit Span data from two different folders and combines them into a single DataFrame. The `identifier` argument is used to specify the column/value tuple to use as an identifier for the data. This is useful for combining data from different timepoints, for example.


```python
from yapi.inquisit import InquisitClient
yiq = InquisitClient(verbose=True)

savepath = "Cognitive Data/Combined Data/"

pvt1_path = "Cognitive Data/PVT"
pvt2_path = "Cognitive Data/Follow Up/PVT"
ds1_path = "Cognitive Data/Digit Span"
ds2_path = "Cognitive Data/Follow Up/Digital Span"

pvt1_summary, pvt1_raw = yiq.collate(pvt1_path, test = 'PVT', identifier=('timepoint', 'baseline'))
pvt2_summary, pvt2_raw = yiq.collate(pvt2_path, test = 'PVT', identifier=('timepoint', 'followup'))
pvt_summary = pd.concat([pvt1_summary, pvt2_summary], ignore_index=True).reset_index(drop=True)
pvt_raw = pd.concat([pvt1_raw, pvt2_raw], ignore_index=True).reset_index(drop=True)
pvt_summary.to_csv(f"{savepath}PVT_combinedSummary.csv", index=False)
pvt_raw.to_csv(f"{savepath}PVT_combinedRaw.csv", index=False)

ds1_summary, ds1_raw = yiq.collate(ds1_path, test = 'Digit Span', identifier=('timepoint', 'baseline'))
ds2_summary, ds2_raw = yiq.collate(ds2_path, test = 'Digit Span', identifier=('timepoint', 'followup'))
ds_summary = pd.concat([ds1_summary, ds2_summary], ignore_index=True).reset_index(drop=True)
ds_raw = pd.concat([ds1_raw, ds2_raw], ignore_index=True).reset_index(drop=True)
ds_summary.to_csv(f"{savepath}DigitSpan_combinedSummary.csv", index=False)
ds_raw.to_csv(f"{savepath}DigitSpan_combinedRaw.csv", index=False)

```

### Sleep Report Scraper

YAPI also has a helper function for scraping sleep study reports. Currently, it is set up to look for .slp folders, .rtf files, and .dat files in order to find any .rft file with the word 'report' in it.

This is a very basic implementation and will need to be adjusted for different file structures, but should be a good starting point.

```python
def sleep_studies():
    from yapi.sleep_studies import SleepStudies
    yss = SleepStudies()
    
    path = 'path/to/sleep/studies'
    savepath="savefolder/sleep_studies.csv"
    
    df = yss.report.collate(path)   # Optional - savepath. Left blank here
                                    # due to further processing below.
    
    for i, row in df.iterrows():
        # Filepath saved in the dataframe is the full path to the file
        # Below is an example of using this to extract the filename and 
        # participant ID.
        df.at[i, 'file'] = row['filepath'].split('\\')[-1]
        df.at[i, 'participant'] = row['filepath'].split('sleep\\')[-1].split('\\')[0]

    df.to_csv(savepath, index=False)
```
