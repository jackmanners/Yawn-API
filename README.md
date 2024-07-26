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

# Verbose mode will print more information to the console and
# is useful for debugging. Will also return responses as response objects, rather than json.

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
yp = YapiClient()
study = 'SAMOSA'

study_participants = yp.withings.participants.get_all(study_name=study)
participant_ids = [participant['lab_id'] for participant in study_participants]

sleeps = yp.withings.sleep.get(participant_ids, as_df=True)

path = '/path/for/epoch/data'

epoch.backup_study_epoch_data(
    study=study, # Required - the name of the study.
    folder=path, # Optional - if False, will create a directory f'{study}_EpochData' in the current working directory. 
                 # If True, will open a file dialog to select the folder. Otherwise, specify the path to the folder.
    verbose=True, # Optional - print more information to the console.
    update=True # Optional - update the epoch data if it already exists, otherwise will skip any existing files in the folder.
)

# Inclusion of the sleep_df argument will combine the timezone information from the sleep data.
# This is not necessary, but can be useful with interpretation. If unsure, it is recommended to include it.
epoch_data = epoch.combine_epoch_data(
    study=study, # Required - the name of the study.
    input_folder=path, # Required - the folder to save the epoch data to.
    output_folder=path, # Optional - the folder to save the epoch data to, defaults to the input folder.
    sleep_df=sleeps, # Optional - the sleep data to include timezone information from. 
                     # If not included, will still combine the epoch data, but will not include timezone information.
    save=True # Optional - save the combined epoch data to a '{study}_epochCombined.csv' file in the output folder.
)

print(epoch_data.head())
```

### RedCap

YAPI also has a number of helper functions for working with the RedCap API.

For example, the below will get all records from a RedCap project, filter out to only includethose that have consented, and then create participant entries in the YawnLabs database for each of them.

```python

token = 'redcap_token'  # Required - the API token for the RedCap project.
yrc = RedcapClient(verbose=False, token=token)
    
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
ypr = RedcapClient(verbose=True, token=s)

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