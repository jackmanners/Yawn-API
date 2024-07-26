import requests

from yapi import snapi

from yapi.snapi.objects.withings import Withings

class YapiClient:
    _instance = None
    
    def __init__(self, credentials=None, **kwargs):
        self._base = "https://www.snapi.space/api/"
        self._access_token = None
        self._headers = {}
        
        self._verbose = kwargs.get("verbose", False)
        
        self._login(credentials)
        
        self.users = snapi.Users(self)
        self.studies = snapi.Studies(self)
        self.participants = snapi.Participants(self)
        
        self.withings = Withings()
        
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(YapiClient, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls, credentials=None, **kwargs):
        if not cls._instance:
            cls(credentials, **kwargs)
        return cls._instance
    
    def _get_creds(self):
        # Get credentials from snapi_credentials.ini in the same directory as this scriptor on path
        # If not found, prompt user for credentials
        
        try:
            with open("snapi_credentials.ini", "r") as f:
                lines = f.readlines()
                credentials = {"username": lines[0].strip(), "password": lines[1].strip()}
        except FileNotFoundError:
            credentials = {}
            # Request username and password from user
            credentials["username"] = input("Username: ")
            credentials["password"] = input("Password: ")
            
            # Save credentials to snapi_credentials.ini            
            with open("snapi_credentials.ini", "w") as f:
                f.write(credentials["username"] + "\n")
                f.write(credentials["password"] + "\n")
        return credentials
        
    def _login(self, credentials):
        if credentials is None:
            credentials = self._get_creds()
        r = requests.post(
            self._base + 'tokens',
            auth = (credentials["username"], credentials["password"])
        )
        if r.status_code == 200:
            print("Login successful")
            self._access_token = r.json()["access_token"]
            self._headers = {"Authorization": "Bearer " + self._access_token}
            return True
        else:
            print("Login failed")
            return False
        
    