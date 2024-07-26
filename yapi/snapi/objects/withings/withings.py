import requests
from . import Sleep

class Withings:
    def __init__(self):
        from yapi import YapiClient
        
        self._yapi = YapiClient.get_instance()
        self._withings_base = self._yapi._base + "participant/"
        self._verbose = self._yapi._verbose
        
        self.sleep = Sleep(self._yapi)