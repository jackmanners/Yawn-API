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