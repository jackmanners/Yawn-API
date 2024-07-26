import requests


class Sleep:
    def __init__(self, yapi):        
        self._yapi = yapi
        self._withings_base = self._yapi._base + "participant/"
        self._verbose = self._yapi._verbose
        
        self.epoch = epoch(self._yapi)
        
        super().__init__()
    
    def get(self, participants, local=True, as_df=False):
        participants = [participants] if isinstance(participants, str) else participants
        responses = []
        
        for participant in participants:
            endpoint = "get_sleep" if not local else "nights"
            url = self._withings_base + str(participant) + "/withings/" + endpoint
            r = requests.get(url, headers=self._yapi._headers)
            responses.append(r if self._verbose else r.json())
            
        if not as_df:
            return responses
        
        import pandas as pd
        df = pd.concat([pd.DataFrame(record) for record in responses], ignore_index=True)
        
        return df
    
    def update(self, participant_id):
        url = self._withings_base + str(participant_id) + "/withings/nights"
        r = requests.post(url, headers=self._yapi._headers)
        
        return r if self._verbose else r.json()
    
    
class epoch:
    def __init__(self, yapi):
        self._yapi = yapi
        self._withings_base = yapi._base + "participant/"
        self._verbose = yapi._verbose
    
    def get(self, participant_id, w_id, verbose=False):
        url = self._withings_base + str(participant_id) + "/withings/epoch/" + str(w_id)
        r = requests.get(url, headers=self._yapi._headers)
        
        return r if self._verbose or verbose else r.json()