import requests

class Studies:
    def __init__(self, yapi):
        self._yapi = yapi
        self._user_base = yapi._base + "study"
        self._verbose = yapi._verbose
        
    def get_all(self):
        r = requests.get(self._user_base, headers=self._yapi._headers)
        return r if self._verbose else r.json()
    
    def get(self, study_name, summary=False):
        r = requests.get(
            self._user_base + "/" + str(study_name) + ("/summary" if summary else ""),
            headers=self._yapi._headers)
        
        return r if self._verbose else r.json()
    
    def create(self, study_data):
        """
        Creates a new study with the given study data.

        Args:
            study_data (dict): A dictionary containing the study data. 
                                It should include, at least, the "name" key.
                                Also, 'using_withings', 'using_fitbit', etc. can be included.

        Returns:
            If the request is successful and the `_verbose` flag is set to `True`, returns the response object.
            Otherwise, returns the JSON response as a dictionary.

        Raises:
            AssertionError: If the "name" key is not present in the `study_data` dictionary.
        """
        assert "name" in study_data

        r = requests.post(
            self._user_base,
            headers=self._yapi._headers, 
            json=study_data)

        return r if self._verbose else r.json()
    
    def delete(self, username):
        r = requests.delete(
            self._user_base + "/" + str(username),
            headers=self._yapi._headers)
        
        return r if self._verbose else r.json()
    
    def link_user(self, study_name, username):
        r = requests.post(
            self._user_base + "/" + str(study_name) + "/" + str(username),
            headers=self._yapi._headers)
        
        return r if self._verbose else r.json()