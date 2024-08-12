import requests


class Sleep:
    def __init__(self, yapi):        
        self._yapi = yapi
        self._withings_base = self._yapi._base + "participant/"
        self._verbose = self._yapi._verbose
        
        self.epoch = epoch(self._yapi)
        
        super().__init__()
    
    def get(self, participants, local=True, as_df=False):
        """
        Retrieves sleep data for the specified participants.

        Args:
            participants (str or list): The participant(s) for which to retrieve sleep data.
            local (bool, optional):     Whether to retrieve data from the local 
                                        database or from the Withings API. Defaults to True.
            as_df (bool, optional):     Whether to return the sleep data as a 
                                        pandas DataFrame. Defaults to False.

        Returns:
            list or pandas.DataFrame:   The sleep data for the specified participants. 
                                        If `as_df` is True, a pandas DataFrame is returned. 
                                        Otherwise, a list of raw responses is returned.

        """
        participants = [participants] if isinstance(participants, str) else participants
        responses = []

        for participant in participants:
            endpoint = "get_sleep" if not local else "nights"
            url = self._withings_base + str(participant) + "/withings/" + endpoint
            r = requests.get(url, headers=self._yapi._headers)
            responses.append(r if self._verbose else r.json())

        if not as_df or self._verbose:
            if self._verbose:
                print("Verbose mode enabled. Returning raw responses.")
            return responses[0] if len(participants) == 1 else responses

        import pandas as pd
        df = pd.concat([pd.DataFrame(record) for record in responses], ignore_index=True)
        
        return df
    
    def update(self, participant_id:str):
        """
        Updates the sleep data for a participant.

        Args:
            participant_id (str): The YawnLabs/SNAPI ID of the participant.

        Returns:
            If verbose is True, returns the response object from the POST request.
            Otherwise, returns the JSON response.
            
        """
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