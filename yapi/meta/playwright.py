from contextlib import contextmanager
from functools import wraps
from playwright.sync_api import Playwright, sync_playwright

@contextmanager
def playwright_context(headless=True, chrome_path=None):
    with sync_playwright() as playwright:
        if chrome_path:
            browser = playwright.chromium.launch(headless=headless, executable_path=chrome_path)
        else:
            browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        yield page
        context.close()
        browser.close()
        
def playwright_wrapper(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with playwright_context(self.headless) as page:
            return func(self, page, *args, **kwargs)
    return wrapper

class PWUtils:
    def __init__(self):
        pass
    
    def go_to_url_and_wait(page, url):
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
    
    def click_button(page, name, timeout=10000):
        page.get_by_role("button", name=name).click(timeout=timeout)
        
    def fill_input(page, placeholder, value):
        page.get_by_placeholder(placeholder, exact=True).click(timeout=10000000)
        page.get_by_placeholder(placeholder, exact=True).fill(value)
        
    def fill_locator(page, locator, value):
        page.locator(locator).click()
        page.locator(locator).fill(value)
        
    def check_label(page, label, timeout=30000):
        page.get_by_label(label).check(timeout=timeout)
        
        
class create_url:
    def __init__(self):
        pass
    
    def withings_login():
        url = "https://account.withings.com/new_workflow/login"
        return url
    
    def withings_linking(self, lab_id, study=None):
        study = study if study else lab_id
    
        url = f"https://account.withings.com/oauth2_user/authorize2?response_type=code&"\
            f"client_id=83070902596cc1b9be5c11254f1641d015fa5e996c237d52b77f473b34b9a5f4&"\
            f"state={lab_id}+{study}&"\
            f"scope=user.info%2Cuser.activity%2Cuser.metrics&"\
            f"redirect_uri=https%3A%2F%2Fwearable-api.herokuapp.com%2Fapi%2Fparticipant%2Fwithings%2Fget_token"
        
        return url
    
    def fitbit_linking(self, lab_id, study=None):
        study = study if study else lab_id

        url = f"https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=238LFY&"\
            f"scope=activity+cardio_fitness+electrocardiogram+heartrate+location+nutrition+"\
            f"oxygen_saturation+profile+respiratory_rate+settings+sleep+social+temperature+weight&"\
            f"code_challenge=TPM1NE0PWwOqAVpw_s11akPa3bcvaRYEda_Xwr0s5lQ&code_challenge_method=S256&"\
            f"state={lab_id}+{study}&prompt=login"
        
        return url

    def create_withings_url(lab_id, study=None):
        study = study if study else lab_id
        
        link_url = f"https://account.withings.com/oauth2_user/authorize2?response_type=code&"\
            f"client_id=83070902596cc1b9be5c11254f1641d015fa5e996c237d52b77f473b34b9a5f4&"\
            f"state={lab_id}+{study}&"\
            f"scope=user.info%2Cuser.activity%2Cuser.metrics&"\
            f"redirect_uri=https%3A%2F%2Fwearable-api.herokuapp.com%2Fapi%2Fparticipant%2Fwithings%2Fget_token"
    
        return link_url