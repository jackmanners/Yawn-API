import requests

class Users:
    def __init__(self, yapi):
        self._yapi = yapi
        self._user_base = yapi._base + "users"
        self._verbose = yapi._verbose
        
    def get_all(self):
        r = requests.get(self._user_base, headers=self._yapi._headers)
        return r if self._verbose else r.json()
    
    def get(self, user_id):
        r = requests.get(self._user_base + "/" + str(user_id), headers=self._yapi._headers)
        return r if self._verbose else r.json()
    
    def create(self, userdata):
        assert "username" in userdata
        assert "password" in userdata
        assert "email" in userdata
        
        r = requests.post(self._user_base, headers=self._yapi._headers, json=userdata)
        
        return r if self._verbose else r.json()
    
    def delete(self, username):
        r = requests.delete(self._user_base + "/" + str(username), headers=self._yapi._headers)
        
        return r if self._verbose else r.json()