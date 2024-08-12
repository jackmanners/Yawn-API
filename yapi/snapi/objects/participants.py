import requests

from yapi.meta.utilities import filter_response

class Participants:
    def __init__(self, yapi):
        self._yapi = yapi
        self._user_base = yapi._base + "participant"
        self._verbose = yapi._verbose
        
    def get_all(self, **kwargs):
        """Retrieves a list of all participants.
        
        Arguments:
            filter_type: The type of filter to apply to the list of participants.
            Currently supports 'equals', '!equals', 'contains', and '!contains'.
        
        Keyword Arguments:
            **kwargs: Optional filters to apply to the list of participants.
            Currently supports filtering by 'lab_id' and 'study_name'.

        Returns:
            _type_: _description_
        """
        r = requests.get(
            self._user_base,
            headers=self._yapi._headers)
        
        # use any kwargs as a filter to return only the participants that match the filter
        if not kwargs:
            return r if self._verbose else r.json()
        
        data = filter_response(r.json(), **kwargs)
        
        return data
    
    def get(self, participant_id):
        r = requests.get(
            self._user_base + "/" + str(participant_id),
            headers=self._yapi._headers)
        
        return r if self._verbose else r.json()
    
    def create(self, participantdata):
        assert "study_name" in participantdata
        
        r = requests.post(
            self._user_base,
            headers=self._yapi._headers, json=participantdata)
        
        return r if self._verbose else r.json()
    
    def edit(self, participant_id, participantdata):
        r = requests.put(
            self._user_base + "/" + str(participant_id),
            headers=self._yapi._headers, json=participantdata)
        
        return r if self._verbose else r.json()
    
    def delete(self, lab_id):
        r = requests.delete(
            self._user_base + "/" + str(lab_id),
            headers=self._yapi._headers)
        
        return r if self._verbose else r.json()