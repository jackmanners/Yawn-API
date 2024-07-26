import requests

server_urls = {
    'flinders': 'https://researchsurvey.flinders.edu.au/api/',
    'adelaide': 'https://redcap.adelaide.edu.au/api/',
}

class RedcapClient:
    def __init__(self, token, verbose=False,
                 server='flinders', base_url=None):
        
        self._verbose = verbose
        self._token = token
        self._base = base_url if base_url else server_urls[server]
        
        self.records = Records(self)
        self.files = Files(self)

        
class Records:
    def __init__(self, redcap):
        self._redcap = redcap
        self._verbose = redcap._verbose
        self._token = redcap._token
        self._base = redcap._base
    
    def get(self, records=[], fields=[], forms=[], events=[]):
        params = {
            'token': self._token,
            'content': 'record',
            'format': 'json',
            'type': 'flat',
            **({'records': records} if records else {}),
            **({'fields': fields} if fields else {}),
            **({'forms': forms} if forms else {}),
            **({'events': events} if events else {})
        }
            
        r = requests.post(self._base, data=params)
        
        return r if self._verbose else r.json()
    
    def add(self, data,
                      overwriteBehavior='normal', forceAutoNumber=False,
                      dateFormat='YMD', returnContent='count'):
        params = {
            'token': self._token,
            'content': 'record',
            'format': 'json',
            'type': 'flat',
            'data': data,
            'overwriteBehavior': overwriteBehavior,
            'forceAutoNumber': forceAutoNumber,
            'dateFormat': dateFormat,
            'returnContent': returnContent
        }
        
        r = requests.post(self._base, data=params)
        
        return r if self._verbose else r.json()
    
class Files:
    def __init__(self, redcap):
        self._redcap = redcap
        self._verbose = redcap._verbose
        self._token = redcap._token
        self._base = redcap._base
    
    def get(self, record_id, field, event=None, repeat_instance=None):
        params = {
            'token': self._token,
            'content': 'file',
            'action': 'export',
            'record': record_id,
            'field': field,
            'returnFormat': 'json',
            **({'event': event} if event else {}),
            **({'repeat_instance': repeat_instance} if repeat_instance else {})
        }
        
        print(params)
        
        r = requests.post(self._base, data=params)
        
        return r if self._verbose else r.json()
    
    def add(self, record_id, field, file, event=None, repeat_instance=None):
        params = {
            'token': self._token,
            'content': 'file',
            'action': 'import',
            'record': record_id,
            'field': field,
            'file': file,
            'returnFormat': 'json',
            **({'event': event} if event else {}),
            **({'repeat_instance': repeat_instance} if repeat_instance else {})
        }
            
        r = requests.post(self._base, data=params)
        
        return r if self._verbose else r.json()
    
    def save(self, response,
             filename:str,
             filepath:str = None):
        
        path = f'{filepath}/' if filepath else ''
        if '.' in filename:
            filename, extension = filename.split('.')
        else:
            extension = response.headers['Content-Type'].split('/')[-1].split(';')[0]
        
        if response.status_code == 200:
            try:
                with open(f'{path}{filename}.{extension}', 'wb') as f:
                    f.write(response.content)
                return True
            except Exception as e:
                if self._verbose:
                    print(e)
                    print(f"Failed to save file to {path}{filename}.{extension}, check path and extension.")
                return False
        else:
            if self._verbose:
                print(response.json())
            return False