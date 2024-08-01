import requests
from . import Sleep, User

class Withings:
    def __init__(self):
        from yapi import YapiClient
        
        self._yapi = YapiClient.get_instance()
        self._withings_base = self._yapi._base + "participant/"
        self._verbose = self._yapi._verbose
        
        self.user = User(self._yapi)
        self.sleep = Sleep(self._yapi)