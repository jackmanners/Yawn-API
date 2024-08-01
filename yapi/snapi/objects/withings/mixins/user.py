import requests
from datetime import datetime

class User:
    def __init__(self, yapi):        
        self._yapi = yapi
        self._base_url = self._yapi._base + "participant/"
        self._verbose = self._yapi._verbose
        
        super().__init__()
    
    def create(self, participant_id, args):
        """
        Create a user with the given information.
        Will only work if the user is an admin.

        Args:
            participant_id (int): The ID of the participant.
            args (dict): A dictionary containing the user information.
                - 'birthdate' (str): The birthdate of the user in 'YYYY-MM-DD' format.
                - 'height' (float): The height of the user in cm.
                - 'weight' (float): The weight of the user in kg.
                - 'shortname' (str): The shortname to display in the app.
                - 'gender' (int): The gender of the user. 0 for male, 1 for female.
                - 'timezone' (str): The timezone of the user in 'Europe/London' format.
                - 'email' (str): The email address for login.

        Returns:
            If self._verbose is True, returns the response object from the POST request.
            Otherwise, returns the JSON response from the POST request.
        """
        # Check if birthdate is in 'YYYY-MM-DD' format and convert unix timestamp
        if isinstance(args['birthdate'], str):
            try:
                birthdate = int(datetime.strptime(args['birthdate'], '%Y-%m-%d').timestamp())
            except ValueError:
                raise ValueError("Birthdate must be in 'YYYY-MM-DD' format.")

        payload = {
            'birthdate': birthdate,         # in unix timestamp
            'height': args['height'],       # in cm
            'weight': args['weight'],       # in kg
            'shortname': args['shortname'], # shortname to display in app (e.g. 'Jack')
            'gender': args['gender'],       # 0: male, 1: female
            'timezone': args['timezone'],   # timezone in 'Europe/London' format (defaults to Australia/Adelaide)
            'email': args['email']          # email address for login, defaults to snapi.space+p<participant.id>@gmail.com
        }

        url = self._base_url + str(participant_id) + "/withings/user"
        r = requests.post(url, headers=self._yapi._headers, json=payload)

        return r if self._verbose else r.json()
        