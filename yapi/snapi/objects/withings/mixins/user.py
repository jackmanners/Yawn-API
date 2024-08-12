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
            'shortname': args['shortname'], # 3-character shortname to display in app (e.g. 'PX1')
            'gender': args['gender'],       # 0: male, 1: female
            'timezone': args['timezone'],   # timezone in 'Europe/London' format (defaults to Australia/Adelaide)
            'email': args['email']          # email address for login, defaults to snapi.space+p<participant.id>@gmail.com
        }
        
        for extra in args:
            if extra not in payload:
                payload[extra] = args[extra]

        url = self._base_url + str(participant_id) + "/withings/user"
        r = requests.post(url, headers=self._yapi._headers, json=payload)

        return r if self._verbose else r.json()
    
    def update_password(self, participant_email, password):
        """
        Update the password for the given participant.

        Args:
            participant_id (int): The ID of the participant.
            password (str): The new password for the participant.

        Returns:
            If self._verbose is True, returns the response object from the POST request.
            Otherwise, returns the JSON response from the POST request.
        """

        from .....meta.playwright import PWUtils as pw
        from .....meta.playwright import playwright_context, create_url
        from .....meta.email import study_email
        
        # set base email as the email, but excluding anything between '+' and '@'
        base_email = participant_email.split('+')[0] + participant_email.split('@')[1]
        ec = study_email(base_email)

        with playwright_context(headless=False) as page:
            pw.go_to_url_and_wait(page, create_url.withings_login())
            pw.click_button(page, "Accept selected")
            pw.fill_input(page, "Email", participant_email)
            pw.click_button(page, "Next")
            page.wait_for_load_state("domcontentloaded")
            
            pw.go_to_url_and_wait(page, ec.get_email(participant_email))
            
            try:
                page.get_by_role("link", name="Or start using the web app").click(timeout=5000)
            except:
                try:
                    pw.check_label(page, "Agree to our Privacy Policy", timeout=5000)
                    pw.check_label(page, "Agree to our Terms of Use")
                    pw.click_button(page, "Next")
                    pw.click_button(page, "Skip")
                    page.get_by_role("link", name="Or start using the web app").click()
                except: 
                    pass
            
            page.locator(".HMIcons_downsm").click(timeout=5000)
            page.get_by_text("Settings").click()
            page.get_by_text("Create a password").click()
            page.wait_for_load_state("domcontentloaded")
            pw.fill_input(page, "New password", password)
            pw.fill_input(page, "Repeat the new password", password)
            pw.click_button(page, "Add")
            page.wait_for_load_state("domcontentloaded")
            page.get_by_text("Save").click()
            page.wait_for_load_state("domcontentloaded")
            
            page.close()
        
        return True
        